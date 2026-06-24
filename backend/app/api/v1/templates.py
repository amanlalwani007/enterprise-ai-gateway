from fastapi import APIRouter, HTTPException, Header, Depends, Query
from sqlalchemy import select, func
from app.db.session import async_session
from app.models.template import PromptTemplate, TemplateVersion, TemplateDeployment, Experiment
from app.core.templates.engine import resolve_template, extract_variables
from app.api.v1.admin import verify_admin
import litellm

router = APIRouter()


@router.post("/templates")
async def create_template(
    name: str = Query(...),
    content: str = Query(...),
    description: str | None = Query(None),
    tags: str | None = Query(None),
    admin: str = Depends(verify_admin),
):
    async with async_session() as session:
        existing = await session.execute(select(PromptTemplate).where(PromptTemplate.name == name))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Template with this name already exists")
        variables = extract_variables(content)
        tmpl = PromptTemplate(
            name=name,
            content=content,
            description=description,
            tags=tags.split(",") if tags else None,
            variables_schema=variables,
            created_by=admin,
        )
        session.add(tmpl)
        await session.commit()
        await session.refresh(tmpl)
        version = TemplateVersion(template_id=tmpl.id, version=1, content=content, created_by=admin)
        session.add(version)
        await session.commit()
    return {"id": tmpl.id, "name": name, "version": 1, "variables": variables}


@router.get("/templates")
async def list_templates(admin: str = Depends(verify_admin)):
    async with async_session() as session:
        result = await session.execute(
            select(PromptTemplate).where(PromptTemplate.is_deleted == False).order_by(PromptTemplate.updated_at.desc())
        )
        templates = result.scalars().all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "version": t.version,
            "tags": t.tags,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in templates
    ]


@router.get("/templates/{template_id}/versions")
async def list_template_versions(template_id: int, admin: str = Depends(verify_admin)):
    async with async_session() as session:
        result = await session.execute(
            select(TemplateVersion).where(TemplateVersion.template_id == template_id).order_by(TemplateVersion.version.desc())
        )
        versions = result.scalars().all()
    return [
        {"id": v.id, "version": v.version, "content": v.content, "created_at": v.created_at.isoformat() if v.created_at else None}
        for v in versions
    ]


@router.post("/templates/{template_id}/versions")
async def create_template_version(
    template_id: int,
    content: str = Query(...),
    admin: str = Depends(verify_admin),
):
    async with async_session() as session:
        tmpl = await session.execute(select(PromptTemplate).where(PromptTemplate.id == template_id))
        tmpl = tmpl.scalar_one_or_none()
        if not tmpl:
            raise HTTPException(status_code=404, detail="Template not found")
        new_version = tmpl.version + 1
        tmpl.content = content
        tmpl.version = new_version
        tmpl.variables_schema = extract_variables(content)
        version = TemplateVersion(template_id=template_id, version=new_version, content=content, created_by=admin)
        session.add(version)
        await session.commit()
    return {"template_id": template_id, "version": new_version}


@router.post("/templates/{template_id}/deploy")
async def deploy_template(
    template_id: int,
    version: int = Query(...),
    alias: str = Query("production"),
    admin: str = Depends(verify_admin),
):
    async with async_session() as session:
        tmpl = await session.execute(select(PromptTemplate).where(PromptTemplate.id == template_id))
        tmpl = tmpl.scalar_one_or_none()
        if not tmpl:
            raise HTTPException(status_code=404, detail="Template not found")
        dep = TemplateDeployment(template_id=template_id, version=version, alias=alias, created_by=admin)
        session.add(dep)
        await session.commit()
    return {"template_id": template_id, "version": version, "alias": alias}


@router.delete("/templates/{template_id}")
async def delete_template(template_id: int, admin: str = Depends(verify_admin)):
    async with async_session() as session:
        tmpl = await session.execute(select(PromptTemplate).where(PromptTemplate.id == template_id))
        tmpl = tmpl.scalar_one_or_none()
        if not tmpl:
            raise HTTPException(status_code=404, detail="Template not found")
        tmpl.is_deleted = True
        await session.commit()
    return {"message": "Template deleted"}


@router.post("/experiments")
async def create_experiment(
    name: str = Query(...),
    template_id: int = Query(...),
    variants: str = Query(...),
    admin: str = Depends(verify_admin),
):
    import json
    parsed = json.loads(variants)
    async with async_session() as session:
        exp = Experiment(name=name, template_id=template_id, variants=parsed)
        session.add(exp)
        await session.commit()
        await session.refresh(exp)
    return {"id": exp.id, "name": name, "status": "running"}


@router.get("/experiments/{experiment_id}")
async def get_experiment(experiment_id: int, admin: str = Depends(verify_admin)):
    async with async_session() as session:
        result = await session.execute(select(Experiment).where(Experiment.id == experiment_id))
        exp = result.scalar_one_or_none()
        if not exp:
            raise HTTPException(status_code=404, detail="Experiment not found")
    return {
        "id": exp.id,
        "name": exp.name,
        "template_id": exp.template_id,
        "variants": exp.variants,
        "status": exp.status,
        "started_at": exp.started_at.isoformat() if exp.started_at else None,
    }


@router.post("/experiments/{experiment_id}/stop")
async def stop_experiment(experiment_id: int, admin: str = Depends(verify_admin)):
    async with async_session() as session:
        exp = await session.execute(select(Experiment).where(Experiment.id == experiment_id))
        exp = exp.scalar_one_or_none()
        if not exp:
            raise HTTPException(status_code=404, detail="Experiment not found")
        exp.status = "stopped"
        from datetime import datetime
        exp.ended_at = datetime.utcnow()
        await session.commit()
    return {"message": "Experiment stopped"}


@router.post("/playground/compare")
async def playground_compare(
    prompt: str = Query(...),
    models: str = Query(...),
    system_prompt: str | None = Query(None),
    temperature: float = Query(0.7),
    max_tokens: int = Query(256),
):
    import json
    model_list = json.loads(models)
    results = []
    for model in model_list:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            results.append({
                "model": model,
                "content": content,
                "tokens": response.usage.total_tokens if response.usage else 0,
                "cost": 0.001,
            })
        except Exception as e:
            results.append({"model": model, "error": str(e)})
    return {"results": results}

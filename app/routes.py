from fastapi import APIRouter, HTTPException
from app.models import Libro
from tortoise.contrib.pydantic import pydantic_model_creator  # Cambiado el origen de la importación

router = APIRouter()

Libro_Pydantic = pydantic_model_creator(Libro)
LibroIn_Pydantic = pydantic_model_creator(Libro, name="LibroIn", exclude_readonly=True)

@router.post("/libros")
async def crear_libro(libro: LibroIn_Pydantic):
    libro_obj = await Libro.create(**libro.dict())
    return await Libro_Pydantic.from_tortoise_orm(libro_obj)

@router.get("/libros")
async def listar_libros():
    return await Libro_Pydantic.from_queryset(Libro.all())

@router.get("/libros/{id}")
async def obtener_libro(id: int):
    libro = await Libro.get_or_none(id=id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return await Libro_Pydantic.from_tortoise_orm(libro)

@router.put("/libros/{id}")
async def actualizar_libro(id: int, libro: LibroIn_Pydantic):
    libro_obj = await Libro.get_or_none(id=id)
    if not libro_obj:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    await Libro.filter(id=id).update(**libro.dict())
    return await Libro_Pydantic.from_queryset_single(Libro.get(id=id))

@router.delete("/libros/{id}")
async def eliminar_libro(id: int):
    deleted = await Libro.filter(id=id).delete()
    if not deleted:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return {"message": "Libro eliminado"}

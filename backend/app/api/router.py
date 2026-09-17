from fastapi import APIRouter

from app.api.routes.contratos_parqueo import router as contratos_parqueo_router
from app.api.routes.espacios import router as espacios_router
from app.api.routes.inquilinos import router as inquilinos_router
from app.api.routes.obligaciones import router as obligaciones_router
from app.api.routes.pagos import router as pagos_router
from app.api.routes.parqueo_temporal import router as parqueo_temporal_router
from app.api.routes.responsables import router as responsables_router
from app.api.routes.vehiculos import router as vehiculos_router


api_router = APIRouter(prefix="/api")
api_router.include_router(responsables_router)
api_router.include_router(inquilinos_router)
api_router.include_router(obligaciones_router)
api_router.include_router(pagos_router)
api_router.include_router(espacios_router)
api_router.include_router(vehiculos_router)
api_router.include_router(contratos_parqueo_router)
api_router.include_router(parqueo_temporal_router)

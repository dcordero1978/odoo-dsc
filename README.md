# odoo-dsc

Módulos personalizados de DSC / ECSESA para **Odoo 19 Community**.

Este repositorio contiene únicamente los módulos custom (addons). El core de Odoo
se mantiene aparte y se actualiza desde el repositorio oficial `odoo/odoo`.

## Estructura

```
odoo-dsc/
└── dsc_base/                  ← módulo base de personalizaciones
    ├── __manifest__.py
    ├── __init__.py
    ├── models/
    │   ├── __init__.py
    │   └── dsc_ejemplo.py
    ├── security/
    │   └── ir.model.access.csv
    └── views/
        └── dsc_base_views.xml
```

## Entornos

| Entorno | Ubicación | Uso |
|---------|-----------|-----|
| Desarrollo | Windows: `E:\DESARROLLO\ContSis\prueba\ContSis\Odoo_DSC` | editar módulos |
| Producción | OCI: `/opt/odoo19/custom-addons/odoo-dsc` | desplegar vía git pull |

- **Odoo producción**: https://dsc-odoo.duckdns.org
- **Servidor**: OCI `erpnext-server` (ARM64), Odoo 19 + Python 3.12 + PostgreSQL 14

## Workflow de desarrollo

### 1. Editar en Windows y subir a GitHub
```powershell
cd E:\DESARROLLO\ContSis\prueba\ContSis\Odoo_DSC
git add .
git commit -m "descripción del cambio"
git push
```

### 2. Desplegar en producción (SSH a OCI)
```bash
ssh ubuntu@129.146.2.44
sudo su - odoo19
cd /opt/odoo19/custom-addons/odoo-dsc
git pull

# Actualizar el módulo en la base de datos (reemplazar NOMBRE_BD)
/opt/odoo19/venv/bin/python /opt/odoo19/odoo/odoo-bin \
  -c /opt/odoo19/odoo.conf -d NOMBRE_BD -u dsc_base --stop-after-init
exit

# Reiniciar el servicio
sudo systemctl restart odoo19
```

> Para instalar un módulo por primera vez usar `-i dsc_base` en lugar de `-u dsc_base`.

## Notas

- El `addons_path` en producción ya incluye `/opt/odoo19/custom-addons`.
  Al clonar aquí, la ruta efectiva del módulo será
  `/opt/odoo19/custom-addons/odoo-dsc/dsc_base`, por lo que hay que asegurarse
  de que Odoo escanee el subdirectorio (ver sección de despliegue en
  `Recursos/odoo-progreso.md`).
- Licencia: LGPL-3 (igual que Odoo Community).

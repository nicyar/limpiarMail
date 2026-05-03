## 🛡️ Cómo agregar un CUIT a la lista negra (blacklist) desde GitHub

Seguí estos simples pasos para bloquear un nuevo CUIT directamente desde el repositorio.

### 1️⃣ Entrar al archivo `app.py`

- En la página principal de tu repositorio, hacé clic en el archivo `app.py`.
- Arriba a la derecha del contenido del archivo, buscá el ícono del ✏️ lápiz que dice **"Edit this file"** y hace clic.

### 2️⃣ Editar la lista negra

- Buscá la sección donde aparece:  
  `cuit_blacklist = [`  
- Agregá el nuevo CUIT respetando las comillas y la coma al final.

### 3️⃣ Guardar los cambios (Commit)

- Hacé clic en el botón verde **"Commit changes..."** (arriba a la derecha).
- En la ventana que aparece:
  - En el primer cuadro (mensaje), poné algo corto como:  
    `Agrego CUIT de [Nombre de la Empresa]`
  - Asegurate de que esté seleccionada la opción  
    ✅ **"Commit directly to the main branch"**
- Hacé clic en el botón verde **"Commit changes"**.

---

🎉 ¡Listo! El nuevo CUIT ya está en la lista negra.

#### 📝 Ejemplo:

```python
"30123456789",  # Nombre de la Empresa

INSTRUCCIONES PARA EJECUTAR EL CHATBOT

1. Instala Python 3.13 (o superior).
2. Abre la terminal y navega a la carpeta del proyecto.
3. Crea un entorno virtual:
   python -m venv venv
4. Actívalo:
   - En Windows: venv\Scripts\activate
   - En macOS/Linux: source venv/bin/activate
5. Instala las dependencias:
   pip install -r requirements.txt
6. Crea un archivo .env con tu API key de OpenRouter:
   OPENROUTER_API_KEY=tu_clave_aqui
7. Ejecuta el servidor:
   python app.py
8. Abre tu navegador en http://localhost:5000

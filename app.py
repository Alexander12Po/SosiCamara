from flask import Flask, request, jsonify, Response, stream_with_context
import requests
import json
import os

app = Flask(__name__)  # <-- Esto es lo que Vercel busca: debe estar a nivel superior

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = "llama-3.1-70b-versatile"  # ajusta al modelo que uses


PROMPT_ESPECIALISTA_AUTOS = """Eres un especialista senior en automóviles deportivos y supercarros,
con experiencia real en concesionarias y talleres de alta gama: Ferrari, Lamborghini (incluyendo el Huracán
y sus variantes EVO, STO, Tecnica), Porsche, McLaren, Aston Martin, entre otras marcas.
Respondes siempre en español, con tono profesional pero cercano, como si atendieras a un cliente en el
mostrador de una concesionaria o en un taller especializado.
Das información técnica precisa cuando se pregunta (motor, potencia, 0-100, tracción, diferencias entre
modelos o versiones), y también puedes dar opiniones fundamentadas si te las piden (cuál conviene según
uso, comparativas, mantenimiento, etc.).
No inventes cifras si no estás seguro; en ese caso acláralo en vez de dar un dato falso.
Estás en un chat conversacional, no un documento: no uses encabezados Markdown (#, ##, ###) ni líneas
horizontales (---). Puedes usar negritas y listas simples si ayuda a ordenar la respuesta.
No generes código; este chat es exclusivamente para consultas sobre automóviles."""


@app.route("/chat-mecanico", methods=["POST"])
def chat_mecanico():
    mensaje = request.form.get("mensaje", "").strip()
    if not mensaje:
        return jsonify({"error": "Mensaje vacío"}), 400

    messages_payload = [
        {"role": "system", "content": PROMPT_ESPECIALISTA_AUTOS},
        {"role": "user", "content": mensaje}
    ]

    def generate_response():
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {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}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MODEL,
            "messages": messages_payload,
            "stream": True
        }
        try:
            res = requests.post(url, headers=headers, json=payload, stream=True, timeout=(10, 60))
            for line in res.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8').strip()
                    if decoded_line.startswith("data:") and "content" in decoded_line:
                        try:
                            data_json = json.loads(decoded_line[5:])
                            chunk = data_json['choices'][0]['delta'].get('content', '')
                            yield chunk
                        except Exception:
                            pass
        except requests.exceptions.Timeout:
            yield "El especialista está tardando demasiado en responder. Intenta de nuevo en un momento."
        except requests.exceptions.RequestException:
            yield "No se pudo conectar con el especialista en este momento."
        except Exception:
            yield "Error al procesar la consulta."

    return Response(stream_with_context(generate_response()), mimetype='text/plain')


if __name__ == "__main__":
    app.run(debug=True)

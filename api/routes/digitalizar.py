import os
import cv2
import logging
from flask import Blueprint, request, jsonify, current_app, make_response
from werkzeug.utils import secure_filename
from config import Config
from services.yolo_processor import analisar_regiao
from services.azure_form import extrair_dados_com_modelo_azure

logger = logging.getLogger(__name__)

digitalizar_bp = Blueprint('digitalizar', __name__)

MAX_FILES = 10

@digitalizar_bp.route('/digitalizar', methods=['POST', 'OPTIONS'])
def digitalizar():
    if request.method == 'OPTIONS':
        return make_response(('', 204))
    files = request.files.getlist('image_files')
    if not files or files[0].filename == '':
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    if len(files) > MAX_FILES:
        return jsonify({'error': f'Máximo de {MAX_FILES} arquivos por requisição.'}), 400

    resultados = []
    salvos = []

    try:
        for file in files:
            if not (file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS):
                logger.warning(f"Arquivo inválido: {file.filename}")
                continue

            nome_seguro = secure_filename(file.filename)
            caminho = os.path.join(Config.UPLOAD_FOLDER, nome_seguro)
            file.save(caminho)
            salvos.append(caminho)

            imagem = cv2.imread(caminho)
            if imagem is None:
                resultados.append({"imagem_processada": nome_seguro, "erro": "Imagem inválida."})
                continue

            h, w, _ = imagem.shape
            from models_loader import model_loader
            yolo_result = model_loader.yolo_model(imagem, verbose=False)[0]
            labels_detectados = {yolo_result.names[int(cls)] for cls in yolo_result.boxes.cls}
            tem_maos = any(l in ['md', 'me'] for l in labels_detectados)
            tem_pes = any(l in ['pd', 'pe'] for l in labels_detectados)

            if tem_maos and tem_pes:
                img_maos = imagem[h//2:, :w//2]
                img_pes = imagem[:h//2, w//2:]
                dados_maos = analisar_regiao(img_maos, 'maos')
                dados_pes = analisar_regiao(img_pes, 'pes')
            elif tem_maos:
                dados_maos = analisar_regiao(imagem[h//2:, :], 'maos')
                dados_pes = {}
            elif tem_pes:
                dados_pes = analisar_regiao(imagem[:h//2, :], 'pes')
                dados_maos = {}
            else:
                fallback = analisar_regiao(imagem, 'ambos')
                dados_maos = {"consultas_maos": fallback.get("consultas_maos", [])}
                dados_pes = {"consultas_pes": fallback.get("consultas_pes", [])}

            dados_azure = extrair_dados_com_modelo_azure(caminho)

            resultados.append({
                "imagem_processada": nome_seguro,
                "dados_documento": dados_azure,
                "analise_sensibilidade": {
                    "consultas_maos": dados_maos.get("consultas_maos", []),
                    "consultas_pes": dados_pes.get("consultas_pes", [])
                }
            })

        if not resultados:
            return jsonify({'error': 'Nenhum arquivo válido foi processado.'}), 400

        return jsonify(resultados[0] if len(resultados) == 1 else resultados)

    except Exception as e:
        logger.error(f"Erro inesperado: {e}", exc_info=True)
        return jsonify({'error': 'Erro interno do servidor.'}), 500

    finally:
        for caminho in salvos:
            if os.path.exists(caminho):
                os.remove(caminho)
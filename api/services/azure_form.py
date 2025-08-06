from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from config import Config
import logging

logger = logging.getLogger(__name__)

client = DocumentAnalysisClient(
    endpoint=Config.AZURE_FORM_RECOGNIZER_ENDPOINT,
    credential=AzureKeyCredential(Config.AZURE_FORM_RECOGNIZER_KEY)
)

def extrair_dados_com_modelo_azure(image_path):
    try:
        with open(image_path, "rb") as f:
            poller = client.begin_analyze_document(model_id=Config.AZURE_CUSTOM_MODEL_ID, document=f)
            result = poller.result()

        dados = {}
        if not result.documents:
            return dados

        for document in result.documents:
            for nome, campo in document.fields.items():
                if campo:
                    if campo.value_type in ("string", "selectionMark"):
                        dados[nome] = campo.value
                    else:
                        dados[nome] = campo.content
                else:
                    dados[nome] = None

        return dados

    except Exception as e:
        logger.error(f"Erro ao processar documento com Azure: {e}", exc_info=True)
        return {"erro_azure": str(e)}
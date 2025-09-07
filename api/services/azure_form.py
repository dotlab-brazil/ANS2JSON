from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from config import Config
import logging

logger = logging.getLogger(__name__)

# Initialize Azure client only if credentials are available
client = None
if Config.AZURE_FORM_RECOGNIZER_ENDPOINT and Config.AZURE_FORM_RECOGNIZER_KEY:
    try:
        client = DocumentAnalysisClient(
            endpoint=Config.AZURE_FORM_RECOGNIZER_ENDPOINT,
            credential=AzureKeyCredential(Config.AZURE_FORM_RECOGNIZER_KEY)
        )
        logger.info("Azure Form Recognizer client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Azure client: {e}")
        client = None
else:
    logger.warning("Azure Form Recognizer credentials not provided, Azure functionality will be disabled")

def extrair_dados_com_modelo_azure(image_path):
    if not client:
        logger.warning("Azure client not available, returning empty data")
        return {"erro_azure": "Azure service not configured"}
        
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
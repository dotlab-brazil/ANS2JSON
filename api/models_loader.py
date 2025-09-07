import joblib
import logging
from ultralytics import YOLO

logger = logging.getLogger(__name__)

class ModelLoader:
    def __init__(self):
        try:
            self.yolo_model = YOLO('ml_models/best.pt')
            logger.info("YOLO model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.yolo_model = None
            
        try:
            self.rf_model = joblib.load('ml_models/random_forest_model.joblib')
            logger.info("Random Forest model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Random Forest model: {e}")
            self.rf_model = None
            
        try:
            self.label_encoder = joblib.load('ml_models/label_encoder.joblib')
            logger.info("Label encoder loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load label encoder: {e}")
            self.label_encoder = None
            
        try:
            self.training_columns = joblib.load('ml_models/rf_feature_columns.joblib')
            logger.info("Training columns loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load training columns: {e}")
            self.training_columns = []
            
        # Handle the case where label_encoder might be loaded but classes attribute is missing
        if self.label_encoder and hasattr(self.label_encoder, 'classes_'):
            self.all_labels = self.label_encoder.classes_
        else:
            self.all_labels = []
            
        self.master_point_list = self._criar_mapeamento_pontos()

    def _criar_mapeamento_pontos(self):
        # Use numpy's size method to check if array is empty
        if self.all_labels is None or (hasattr(self.all_labels, 'size') and self.all_labels.size == 0):
            return {}
        return {
            'md': [l for l in self.all_labels if 'direito' not in l and 'esquerdo' not in l],
            'me': [l for l in self.all_labels if 'direito' not in l and 'esquerdo' not in l],
            'pd': [l for l in self.all_labels if l.endswith('_direito')],
            'pe': [l for l in self.all_labels if l.endswith('_esquerdo')]
        }

# Instância global para importar nos serviços
model_loader = ModelLoader()
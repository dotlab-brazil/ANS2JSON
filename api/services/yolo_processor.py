import math
import pandas as pd
from models_loader import model_loader

def classificar_ponto(membro, ponto, bbox_membro, aspect_ratio, limb_area):
    lx1, ly1, lx2, ly2 = bbox_membro
    pw, ph = ponto['box'][2] - ponto['box'][0], ponto['box'][3] - ponto['box'][1]
    point_area = pw * ph if pw > 0 and ph > 0 else 0
    dx = ponto['center'][0] - membro['center'][0]
    dy = ponto['center'][1] - membro['center'][1]
    dist = math.sqrt(dx**2 + dy**2)

    dados = pd.DataFrame([{
        'membro_tipo': membro['label'],
        'cor_detectada': ponto['label'],
        'distancia_ao_centro_membro': dist,
        'ponto_centro_x_relativo': (ponto['center'][0] - lx1) / (lx2 - lx1),
        'ponto_centro_y_relativo': (ponto['center'][1] - ly1) / (ly2 - ly1),
        'area_relativa_ponto': point_area / limb_area,
        'aspect_ratio_membro': aspect_ratio,
        'conf_ponto': ponto['confidence'],
        'conf_membro': membro['confidence']
    }])

    dados = pd.get_dummies(dados, columns=['membro_tipo', 'cor_detectada'])
    dados = dados.reindex(columns=model_loader.training_columns, fill_value=0)
    pred = model_loader.rf_model.predict(dados)
    return model_loader.label_encoder.inverse_transform(pred)[0]

def analisar_regiao(imagem_np, tipo_regiao):
    results = model_loader.yolo_model(imagem_np, verbose=False)[0]
    limbs, points = [], []

    for box in results.boxes.data.tolist():
        label = results.names[int(box[5])]
        detection = {
            'label': label,
            'box': box[:4],
            'confidence': box[4],
            'center': ((box[0]+box[2])/2, (box[1]+box[3])/2)
        }
        if label in {'md', 'me', 'pd', 'pe'}:
            limbs.append(detection)
        else:
            points.append(detection)

    grupos = {
        "maos": ['md', 'me'],
        "pes": ['pd', 'pe'],
        "ambos": ['md', 'me', 'pd', 'pe']
    }
    selecionados = [(k, v) for k, v in grupos.items() if tipo_regiao in (k, "ambos")]

    saida = {"consultas_maos": [], "consultas_pes": []}
    for tipo, labels in selecionados:
        membros = sorted([l for l in limbs if l['label'] in labels], key=lambda m: m['box'][0])
        for i in range(0, len(membros), 2):
            consulta = {"consulta_id": (i//2)+1, "membros": []}
            for membro in membros[i:i+2]:
                lx1, ly1, lx2, ly2 = [int(v) for v in membro['box']]
                membro_points = [p for p in points if lx1 <= p['center'][0] <= lx2 and ly1 <= p['center'][1] <= ly2]
                aspect = (lx2 - lx1) / (ly2 - ly1)
                limb_area = (lx2 - lx1) * (ly2 - ly1)
                esperados = model_loader.master_point_list.get(membro['label'], {})
                mapeados = {e: "Não identificado" for e in esperados}

                for ponto in membro_points:
                    nome_pred = classificar_ponto(membro, ponto, (lx1, ly1, lx2, ly2), aspect, limb_area)
                    if nome_pred in mapeados:
                        mapeados[nome_pred] = ponto['label']

                consulta["membros"].append({
                    "tipo_membro": membro['label'],
                    "pontos_mapeados": mapeados
                })
            saida[f"consultas_{tipo}"] += [consulta]

    return saida
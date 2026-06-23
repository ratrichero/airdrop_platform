from datetime import datetime

def apply_decay(score, created_at):

    days_old = (datetime.utcnow() - created_at).days

    decay_factor = 1 - (days_old * 0.02)  # 2% mỗi ngày

    if decay_factor < 0.5:
        decay_factor = 0.5

    return round(score * decay_factor, 2)
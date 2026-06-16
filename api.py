from flask import Blueprint, request, jsonify, send_from_directory
import os
from datetime import datetime, timedelta

try:
    from backend.scada_server.auth_utils import auth_required
except ImportError:
    try:
        from ..scada_server.auth_utils import auth_required
    except ImportError:
        from auth_utils import auth_required

forecasting_bp = Blueprint('forecasting', __name__)

# Lazy initialization - manager створюється тільки коли потрібен
# Це дозволяє серверу запуститись навіть якщо pandas відсутній
_manager = None
_base_dir = None

def get_manager():
    """Отримує або створює ForecastingManager (lazy initialization)"""
    global _manager, _base_dir
    if _manager is None:
        try:
            from .forecasting_core import ForecastingManager
            if _base_dir is None:
                _base_dir = os.path.dirname(os.path.abspath(__file__))
            _manager = ForecastingManager(_base_dir)
        except ImportError as e:
            if 'pandas' in str(e).lower():
                raise ImportError("Forecasting requires pandas. Install it or disable forecasting module.")
            raise
    return _manager

@forecasting_bp.route('/update_rdn', methods=['POST'])
@auth_required(role='admin')
def update_rdn():
    data = request.json
    date_str = data.get('date')
    market_type = data.get('market_type', 'DAM')
    
    if not date_str:
        return jsonify({'success': False, 'message': 'Date is required'}), 400
        
    try:
        mgr = get_manager()
        # Fetch data
        results = mgr.fetch_oree_data(date_str, market_type)
        if results:
            success = mgr.update_csv(results, date_str, market_type)
            if success:
                return jsonify({'success': True, 'message': f'Successfully updated {market_type} data for {date_str}'})
            else:
                return jsonify({'success': False, 'message': 'Failed to update CSV file'})
        else:
            return jsonify({'success': False, 'message': 'No data found on OREE website'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@forecasting_bp.route('/update_weather', methods=['POST'])
@auth_required(role='admin')
def update_weather():
    data = request.json
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not start_date or not end_date:
        # Default to today + 4 days
        start_date = datetime.now().strftime("%d.%m.%Y")
        end_date = (datetime.now() + timedelta(days=4)).strftime("%d.%m.%Y")
        
    try:
        mgr = get_manager()
        weather_data = mgr.fetch_weather_data(start_date, end_date)
        if weather_data is not None:
            success = mgr.update_weather_csv(weather_data)
            if success:
                return jsonify({'success': True, 'message': 'Weather data updated successfully'})
            else:
                return jsonify({'success': False, 'message': 'No changes made to CSV'})
        else:
            return jsonify({'success': False, 'message': 'Failed to fetch weather data'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@forecasting_bp.route('/train', methods=['POST'])
@auth_required(role='admin')
def train_model():
    try:
        mgr = get_manager()
        success, output = mgr.run_script("train_model_v1.py")
        return jsonify({'success': success, 'message': output})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@forecasting_bp.route('/predict', methods=['POST'])
@auth_required()
def predict():
    data = request.json
    date_str = data.get('date')
    
    if not date_str:
        return jsonify({'success': False, 'message': 'Date is required'}), 400
        
    try:
        mgr = get_manager()
        success, output = mgr.run_script("predict_tomorrow_v1.py", args=[date_str])
        
        image_url = None
        if success:
            image_candidates = ["prediction_tomorrow.png", "prediction_plot_v1.png"]
            for image_name in image_candidates:
                if os.path.exists(os.path.join(mgr.output_dir, image_name)):
                    image_url = f"/api/forecasting/image/{image_name}"
                    break
                
        return jsonify({'success': success, 'message': output, 'image_url': image_url})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@forecasting_bp.route('/compare', methods=['POST'])
@auth_required()
def compare():
    data = request.json
    date_str = data.get('date')
    
    if not date_str:
        return jsonify({'success': False, 'message': 'Date is required'}), 400
        
    try:
        mgr = get_manager()
        success, output = mgr.run_script("update_and_compare_v1.py", args=[date_str])
        
        image_url = None
        if success:
            if os.path.exists(os.path.join(mgr.output_dir, "comparison_latest.png")):
                image_url = "/api/forecasting/image/comparison_latest.png"
                
        return jsonify({'success': success, 'message': output, 'image_url': image_url})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@forecasting_bp.route('/evaluate', methods=['POST'])
@auth_required()
def evaluate():
    try:
        mgr = get_manager()
        success, output = mgr.run_script("evaluate_long_term_v1.py")
        image_url = None
        if success and os.path.exists(os.path.join(mgr.output_dir, "evaluation_improved.png")):
            image_url = "/api/forecasting/image/evaluation_improved.png"
        return jsonify({'success': success, 'message': output, 'image_url': image_url})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@forecasting_bp.route('/features', methods=['POST'])
@auth_required()
def features():
    try:
        mgr = get_manager()
        success, output = mgr.run_script("check_feature_importance_v1.py")
        image_url = None
        if success and os.path.exists(os.path.join(mgr.output_dir, "feature_importance.png")):
            image_url = "/api/forecasting/image/feature_importance.png"
        return jsonify({'success': success, 'message': output, 'image_url': image_url})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@forecasting_bp.route('/delete_models', methods=['POST'])
@auth_required(role='admin')
def delete_models():
    try:
        import glob
        mgr = get_manager()
        files = glob.glob(os.path.join(mgr.models_dir, "*"))
        count = 0
        for f in files:
            try:
                os.remove(f)
                count += 1
            except:
                pass
        return jsonify({'success': True, 'message': f'Deleted {count} model files'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@forecasting_bp.route('/image/<filename>')
def get_image(filename):
    mgr = get_manager()
    return send_from_directory(mgr.output_dir, filename)

@forecasting_bp.route('/send_telegram', methods=['POST'])
@auth_required()
def send_telegram():
    data = request.json
    image_url = data.get('image_url')
    caption = data.get('caption')
    
    if not image_url:
        return jsonify({'success': False, 'message': 'Image URL is required'}), 400

    mgr = get_manager()
    filename = image_url.split('/')[-1]
    file_path = os.path.join(mgr.output_dir, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': 'File not found'}), 404
        
    # Load config from env
    chat_id = os.getenv('TELEGRAM_GROUP_ID') or "-1002275461964"
    thread_id = os.getenv('TELEGRAM_GROUP_THREAD_ID') or "835"
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
         return jsonify({'success': False, 'message': 'Telegram Bot Token not configured'}), 500
         
    try:
        from scada_core.utils.telegram_notifier import TelegramNotifier
        notifier = TelegramNotifier(bot_token, int(chat_id))
        
        with open(file_path, 'rb') as f:
            photo_bytes = f.read()
            
        success = notifier.send_photo_sync(photo_bytes, caption, thread_id=int(thread_id))
        
        if success:
            return jsonify({'success': True, 'message': 'Sent to Telegram'})
        else:
             return jsonify({'success': False, 'message': 'Failed to send to Telegram'}), 500
             
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

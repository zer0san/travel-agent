from flask import Blueprint, jsonify, request
from app.agent.agents import get_planner_agent
from app.service.unsplash_service import get_unsplash_service
from app.model.TripPlanRequest import TripPlanRequest
main_bp = Blueprint('main', __name__, url_prefix='/api')

@main_bp.route('/generate-trip-plan', methods=['POST'])
async def generate_trip_plan():
    payload = request.get_json(silent=True) or {}
    trip_request = TripPlanRequest.model_validate(payload)
    planner_agent = await get_planner_agent()
    result = await planner_agent.plan_trip(trip_request)

    if hasattr(result, "model_dump"):
        result = result.model_dump()

    return jsonify({"result": result})

@main_bp.route('/get_attraction_photos', methods=['GET'])
def get_attraction_photos():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "missing query parameter: name"}), 400

    unsplash_service = get_unsplash_service()
    imgs = unsplash_service.search_photos(name)
    return jsonify(imgs)

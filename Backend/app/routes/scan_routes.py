from flask import Blueprint, request, jsonify
from ..services.scan_services import ScanService

scan_bp = Blueprint('scan', __name__)

@scan_bp.route('', methods=['POST'])
def create_scan():
    try:
        new_scan = ScanService.create_scan(request.json)
        return jsonify({'message': 'Scan created successfully', 'id': new_scan.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@scan_bp.route('', methods=['GET'])
def get_scans():
    scans = ScanService.get_all_scans()
    return jsonify([scan.to_dict() for scan in scans])

@scan_bp.route('/<int:id>', methods=['GET'])
def get_scan(id):
    scan = ScanService.get_scan_by_id(id)
    return jsonify(scan.to_dict())

@scan_bp.route('/<int:id>', methods=['DELETE'])
def delete_scan(id):
    try:
        scan = ScanService.get_scan_by_id(id)
        ScanService.delete_scan(scan)
        return jsonify({'message': 'Scan deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
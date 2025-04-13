from flask import Blueprint, request, jsonify, send_file
from ..services.scan_services import ScanService
import os

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
    # pour debug
    result = [scan.to_dict() for scan in scans]
    print(f"Found {len(result)} scans")
    return jsonify(result)

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


@scan_bp.route('/download-report/<int:id>', methods=['GET'])
def download_report(id):
    try:
        scan = ScanService.get_scan_by_id(id)
        if not scan.report_pdf:
            return jsonify({'error': 'No report available for this scan'}), 404
            
        # Get the absolute path to the PDF
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Try exact path stored in database
        pdf_path = os.path.join(base_dir, scan.report_pdf.replace('../', ''))
        print(f"Looking for PDF at: {pdf_path}")

        # Try all possible paths - including project root level
        possible_paths = [
            # Inside backend directory
            pdf_path,
            os.path.join(base_dir, 'reports', f"client_{scan.client_id}_scan_{scan.id}.pdf"),
            
            # At project root level (one level up from backend)
            os.path.join(os.path.dirname(base_dir), 'reports', f"client_{scan.client_id}_scan_{scan.id}.pdf")
        ]
        
        # Try each path
        for path in possible_paths:
            print(f"Checking path: {path}")
            if os.path.exists(path):
                pdf_path = path
                print(f"Found PDF at: {pdf_path}")
                
                # Update database with correct relative path
                project_root = os.path.dirname(base_dir)
                rel_path = os.path.relpath(pdf_path, project_root)
                scan.report_pdf = rel_path
                from domain.models import db
                db.session.commit()
                break
        else:
            # If no paths worked, try generic search for any client file
            reports_dir_backend = os.path.join(base_dir, 'reports')
            reports_dir_root = os.path.join(os.path.dirname(base_dir), 'reports')
            
            # Check both possible reports directories
            for reports_dir in [reports_dir_backend, reports_dir_root]:
                if os.path.exists(reports_dir):
                    client_pattern = f"client_{scan.client_id}_scan_"
                    pdf_files = [f for f in os.listdir(reports_dir) if f.startswith(client_pattern)]
                    
                    if pdf_files:
                        pdf_files.sort(key=lambda f: os.path.getmtime(os.path.join(reports_dir, f)), reverse=True)
                        newest_file = pdf_files[0]
                        pdf_path = os.path.join(reports_dir, newest_file)
                        print(f"Found newest file: {pdf_path}")
                        
                        # Update database with correct path
                        project_root = os.path.dirname(base_dir)
                        rel_path = os.path.relpath(pdf_path, project_root)
                        scan.report_pdf = rel_path
                        from domain.models import db
                        db.session.commit()
                        break
            else:
                return jsonify({'error': f'No PDF files found for client {scan.client_id}'}), 404

        # Send the file
        filename = os.path.basename(pdf_path)
        print(f"Sending file: {pdf_path} with download name: {filename}")
        
        response = send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
        # Add headers to prevent caching
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        
        return response
    
    except Exception as e:
        print(f"Error in download_report: {str(e)}")
        return jsonify({'error': str(e)}), 400
    
    

@scan_bp.route('/status/<int:client_id>/latest', methods=['GET'])
def check_latest_scan_status(client_id):
    try:
        latest_scan = ScanService.get_latest_scan_for_client(client_id)
        
        if not latest_scan:
            return jsonify({'status': 'no_scan', 'message': 'No scans found for this client'}), 404
            
        # Check if the scan record has a PDF path
        if latest_scan.report_pdf:
            # IMPORTANT: Check if the file actually exists on disk
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            pdf_path = os.path.join(base_dir, latest_scan.report_pdf.replace('../', ''))
            
            # Alternative paths to check
            alt_paths = [
                pdf_path,
                os.path.join(base_dir, latest_scan.report_pdf),
                os.path.join(base_dir, 'reports', f"client_{latest_scan.client_id}_scan_{latest_scan.id}.pdf")
            ]
            
            file_exists = any(os.path.exists(path) for path in alt_paths)
            
            if file_exists:
                return jsonify({
                    'status': 'complete',
                    'scan_id': latest_scan.id,
                    'report_url': f"/api/scans/download-report/{latest_scan.id}"
                })
            else:
                # PDF path is in DB but file doesn't exist yet
                return jsonify({
                    'status': 'processing',
                    'scan_id': latest_scan.id,
                    'message': 'Scan is processed but report is still being generated'
                })
        else:
            return jsonify({
                'status': 'in_progress',
                'scan_id': latest_scan.id,
                'message': 'Scan is still in progress'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 400
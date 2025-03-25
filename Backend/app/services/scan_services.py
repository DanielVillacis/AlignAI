from domain.models import db
from domain.entities import Scan

class ScanService:
    @staticmethod
    def create_scan(data):
        new_scan = Scan(
            client_id=data['client_id'],
            scan_reason=data['scan_reason']
        )
        db.session.add(new_scan)
        db.session.commit()
        return new_scan

    @staticmethod
    def get_all_scans():
        return Scan.query.all()

    @staticmethod
    def get_scan_by_id(id):
        return Scan.query.get_or_404(id)

    @staticmethod
    def delete_scan(scan):
        db.session.delete(scan)
        db.session.commit()
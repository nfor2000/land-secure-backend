import math
from typing import List, Dict, Tuple

class SimpleGeometry:
    """Minimal geometry calculations"""
    
    EARTH_RADIUS = 6371000  # meters
    
    def points_to_list(self, coords: List[Dict]) -> List[Tuple[float, float]]:
        """Convert dict coordinates to list of tuples"""
        return [(c['lat'], c['lng']) for c in coords]
    
    def calculate_centroid(self, points: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Simple centroid calculation"""
        if not points:
            return (0, 0)
        
        lats = [p[0] for p in points]
        lngs = [p[1] for p in points]
        return (sum(lats)/len(lats), sum(lngs)/len(lngs))
    
    def haversine_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Distance between two points in meters"""
        lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return self.EARTH_RADIUS * c
    
    def polygon_area(self, points: List[Tuple[float, float]]) -> float:
        """Area using shoelace formula"""
        if len(points) < 3:
            return 0.0
        
        area = 0.0
        n = len(points)
        
        for i in range(n):
            j = (i + 1) % n
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        
        return abs(area) / 2.0
    
    def compare_polygons(self, poly1: List[Tuple[float, float]], 
                        poly2: List[Tuple[float, float]]) -> Dict:
        """
        Simple polygon comparison with 3 checks:
        1. Centroid distance
        2. Area similarity
        3. Bounding box overlap
        """
        # 1. Centroid distance
        centroid1 = self.calculate_centroid(poly1)
        centroid2 = self.calculate_centroid(poly2)
        distance = self.haversine_distance(centroid1, centroid2)
        
        # 2. Area similarity
        area1 = self.polygon_area(poly1)
        area2 = self.polygon_area(poly2)
        
        if area2 == 0:
            area_ratio = 0.0
        else:
            area_ratio = min(area1, area2) / max(area1, area2)
        
        # 3. Bounding box overlap (simplified)
        def get_bbox(points):
            lats = [p[0] for p in points]
            lngs = [p[1] for p in points]
            return (min(lats), min(lngs), max(lats), max(lngs))
        
        bbox1 = get_bbox(poly1)
        bbox2 = get_bbox(poly2)
        
        # Check if bboxes intersect
        bbox_overlap = not (bbox1[2] < bbox2[0] or bbox2[2] < bbox1[0] or
                           bbox1[3] < bbox2[1] or bbox2[3] < bbox1[1])
        
        # Simple scoring
        passes = 0
        if distance <= 10:  # 10 meters
            passes += 1
        if area_ratio >= 0.9:  # 90% area match
            passes += 1
        if bbox_overlap:
            passes += 1
        
        # Match if 2 out of 3 pass
        coordinates_match = passes >= 2
        
        return {
            'match': coordinates_match,
            'distance_meters': distance,
            'area_ratio': area_ratio,
            'bbox_overlap': bbox_overlap,
            'passes': passes
        }

# Global instance
geometry = SimpleGeometry()
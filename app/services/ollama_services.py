"""
Optional: Use Ollama only for fraud analysis, not geometry
"""

class OllamaAnalyzer:
    def __init__(self):
        self.enabled = False  # Disable by default
        # Set to True if Ollama is installed
    
    def analyze_fraud_pattern(self, verification_data: dict) -> str:
        """Analyze potential fraud patterns (optional)"""
        if not self.enabled:
            return "Ollama analysis disabled"
        
        # Simple pattern detection without AI
        reasons = []
        
        if verification_data.get('distance_meters', 0) > 100:
            reasons.append("Large coordinate discrepancy (>100m)")
        
        if verification_data.get('overlap_score', 0) < 0.5:
            reasons.append("Low area overlap (<50%)")
        
        if verification_data.get('is_fraud'):
            reasons.append("Location information mismatch")
        
        return ", ".join(reasons) if reasons else "No obvious fraud patterns"

# Global instance
analyzer = OllamaAnalyzer()
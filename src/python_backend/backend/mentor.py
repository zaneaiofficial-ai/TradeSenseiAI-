"""
AI Mentor reasoning module - uses OpenAI GPT to generate trading advice.
"""
import os
from openai import OpenAI

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Initialize client lazily to avoid startup errors if API key is missing
_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        _client = OpenAI(api_key=api_key)
    return _client

def get_mentor_response(user_input: str, trading_context: dict = None, conversation_history: list = None, vision_context: dict = None, language: str = 'en', openai_key: str = None, elevenlabs_key: str = None) -> str:
    """
    Generate AI mentor response based on user input, trading context, conversation history, and vision analysis.
    Supports multiple languages and user-provided API keys.
    """
    try:
        # Use provided key or fallback to env
        api_key = openai_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            return "OpenAI API key required. Please provide your API key in the app settings."
        
        client = OpenAI(api_key=api_key)
        context_str = ""
        if trading_context:
            context_str = f"""
Current Trading Context:
- Asset: {trading_context.get('asset', 'Unknown')}
- Current Price: ${trading_context.get('price', '?')}
- Short MA: {trading_context.get('sma_short', '?')}
- Long MA: {trading_context.get('sma_long', '?')}
- Trend Slope: {trading_context.get('slope', '?')}
"""
        
        vision_str = ""
        if vision_context:
            patterns = vision_context.get('patterns', [])
            indicators = vision_context.get('indicators', {})
            vision_str = f"""
Vision Analysis:
- Detected Patterns: {', '.join(patterns) if patterns else 'None'}
- Indicators: {indicators if indicators else 'None'}
"""
        
        # Language-specific system prompt
        lang_prompts = {
            'en': """You are TradeSensei, an expert AI trading mentor. Your role is to:
1. Provide concise, actionable trading advice
2. Explain chart patterns and indicators from vision analysis
3. Help traders manage risk and emotions
4. Suggest entry/exit strategies based on technical analysis and visual data
5. Keep responses brief (1-2 sentences max for voice chat)
6. Remember previous conversation context for personalized advice

Be direct, professional, and focus on practical trading wisdom.""",
            'es': """Eres TradeSensei, un mentor de trading AI experto. Tu rol es:
1. Proporcionar consejos de trading concisos y accionables
2. Explicar patrones de gráficos e indicadores del análisis visual
3. Ayudar a los traders a gestionar riesgos y emociones
4. Sugerir estrategias de entrada/salida basadas en análisis técnico y datos visuales
5. Mantener respuestas breves (máximo 1-2 oraciones para chat de voz)
6. Recordar el contexto de conversación anterior para consejos personalizados

Sé directo, profesional y enfócate en la sabiduría práctica de trading.""",
            'fr': """Vous êtes TradeSensei, un mentor de trading IA expert. Votre rôle est de:
1. Fournir des conseils de trading concis et actionnables
2. Expliquer les patterns de graphique et indicateurs de l'analyse visuelle
3. Aider les traders à gérer les risques et émotions
4. Suggérer des stratégies d'entrée/sortie basées sur l'analyse technique et données visuelles
5. Garder les réponses brèves (maximum 1-2 phrases pour chat vocal)
6. Se souvenir du contexte de conversation précédent pour des conseils personnalisés

Soyez direct, professionnel et concentrez-vous sur la sagesse pratique du trading."""
        }
        
        system_prompt = lang_prompts.get(language, lang_prompts['en'])
        
        # Build conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-10:]:  # Limit to last 10 messages to avoid token limits
                messages.append(msg)
        
        # Add current context and user input
        combined_context = context_str + vision_str
        if combined_context.strip():
            messages.append({"role": "system", "content": f"Current analysis: {combined_context.strip()}"})
        
        messages.append({"role": "user", "content": user_input})

        # Allow model override via env var to support accounts without gpt-4-mini
        model_name = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"I encountered an error processing your request: {str(e)}"

def get_quick_advice(signal_type: str) -> str:
    """Get quick pre-canned advice for common signals (BUY/SELL/HOLD)."""
    advice_map = {
        "BUY": "Strong buy signal detected. Consider entering a long position with proper risk management.",
        "SELL": "Sell signal triggered. Lock in profits or exit losing positions.",
        "HOLD": "Market shows consolidation. Wait for clearer signals before acting.",
        "NEUTRAL": "No strong signals right now. Stay patient and focused on your trading plan."
    }
    return advice_map.get(signal_type, "Waiting for clearer market conditions.")

def calculate_position_size(account_balance: float, risk_per_trade: float, entry_price: float, stop_loss_price: float) -> dict:
    """
    Calculate position size based on risk management principles.
    Returns position size in units/shares and dollar amount.
    """
    risk_amount = account_balance * (risk_per_trade / 100)
    risk_per_share = abs(entry_price - stop_loss_price)
    if risk_per_share == 0:
        return {"error": "Stop loss must be different from entry price"}
    
    position_size = risk_amount / risk_per_share
    position_value = position_size * entry_price
    
    return {
        "position_size": round(position_size, 2),
        "position_value": round(position_value, 2),
        "risk_amount": round(risk_amount, 2),
        "risk_per_trade_percent": risk_per_trade
    }

def get_risk_management_advice(account_balance: float, current_positions: list = None) -> str:
    """
    Provide risk management advice based on account balance and positions.
    """
    try:
        total_exposure = sum(pos.get('value', 0) for pos in (current_positions or []))
        exposure_ratio = (total_exposure / account_balance) * 100 if account_balance > 0 else 0
        
        advice = f"Account Balance: ${account_balance:.2f}. "
        if exposure_ratio > 20:
            advice += "High exposure detected. Consider reducing positions to manage risk."
        elif exposure_ratio > 10:
            advice += "Moderate exposure. Monitor closely."
        else:
            advice += "Low exposure. Good for adding positions."
        
        advice += f" Current exposure: {exposure_ratio:.1f}% of account."
        return advice
    except Exception as e:
        return f"Error calculating risk: {str(e)}"

if __name__ == '__main__':
    # Test the mentor module
    print("Testing TradeSensei Mentor...")
    
    # Test quick advice
    print("Quick advice for BUY:", get_quick_advice("BUY"))
    
    # Test mentor response (requires API key)
    try:
        response = get_mentor_response("What's a good entry strategy for this chart?")
        print("Mentor response:", response)
    except Exception as e:
        print("Error:", e)

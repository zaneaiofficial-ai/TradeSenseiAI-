using System.Configuration;

namespace TradeSensei.UI
{
    public static class ApiConfig
    {
        private static readonly string _baseUrl = ConfigurationManager.AppSettings["ApiBaseUrl"] ?? "http://127.0.0.1:8000";
        private static readonly string _openAiKey = ConfigurationManager.AppSettings["OpenAiApiKey"] ?? "";
        private static readonly string _elevenLabsKey = ConfigurationManager.AppSettings["ElevenLabsApiKey"] ?? "";

        public static string BaseUrl => _baseUrl;
        public static string OpenAiApiKey => _openAiKey;
        public static string ElevenLabsApiKey => _elevenLabsKey;

        public static string GetFullUrl(string endpoint)
        {
            return $"{_baseUrl.TrimEnd('/')}/{endpoint.TrimStart('/')}";
        }

        public static string GetApiBaseUrl()
        {
            return _baseUrl;
        }

        public static string GetWebSocketUrl()
        {
            return _baseUrl.Replace("http://", "ws://").Replace("https://", "wss://") + "/ws";
        }
    }
}
using System;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

namespace TradeSensei.UI.Networking
{
    public class WebSocketClient : IDisposable
    {
        private ClientWebSocket? socket;
        private CancellationTokenSource cts = new CancellationTokenSource();
        private readonly Uri serverUri;

        public event Action<JsonElement>? OnJsonMessage;

        public WebSocketClient(string uri)
        {
            serverUri = new Uri(uri);
        }

        public async Task ConnectAsync()
        {
            socket = new ClientWebSocket();
            await socket.ConnectAsync(serverUri, CancellationToken.None);
            _ = Task.Run(ReceiveLoop);
        }

        public async Task SendStringAsync(string message)
        {
            if (socket == null || socket.State != WebSocketState.Open) return;
            var bytes = Encoding.UTF8.GetBytes(message);
            await socket.SendAsync(new ArraySegment<byte>(bytes), WebSocketMessageType.Text, true, CancellationToken.None);
        }

        public async Task SendBinaryAsync(byte[] bytes)
        {
            if (socket == null || socket.State != WebSocketState.Open) return;
            await socket.SendAsync(new ArraySegment<byte>(bytes), WebSocketMessageType.Binary, true, CancellationToken.None);
        }

        private async Task ReceiveLoop()
        {
            var buffer = new byte[64 * 1024];
            try
            {
                while (!cts.IsCancellationRequested && socket != null && socket.State == WebSocketState.Open)
                {
                    var seg = new ArraySegment<byte>(buffer);
                    var result = await socket.ReceiveAsync(seg, cts.Token);
                    if (result.MessageType == WebSocketMessageType.Close)
                    {
                        await socket.CloseAsync(WebSocketCloseStatus.NormalClosure, "", CancellationToken.None);
                        break;
                    }

                    var msg = Encoding.UTF8.GetString(buffer, 0, result.Count);
                    try
                    {
                        var doc = JsonDocument.Parse(msg);
                        OnJsonMessage?.Invoke(doc.RootElement);
                    }
                    catch
                    {
                        // ignore non-json messages
                    }
                }
            }
            catch (OperationCanceledException) { }
            catch (Exception) { }
        }

        public void Dispose()
        {
            try { cts.Cancel(); } catch { }
            socket?.Dispose();
        }
    }
}

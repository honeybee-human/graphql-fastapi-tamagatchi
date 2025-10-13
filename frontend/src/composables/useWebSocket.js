import { ref } from 'vue';

export function useWebSocket(currentUser) {
  const ws = ref(null);

  const connectWebSocket = () => {
    if (!currentUser.value) return;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/${currentUser.value.id}`;
    ws.value = new WebSocket(wsUrl);
  };

  const sendMousePosition = (x, y) => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) return;
    ws.value.send(JSON.stringify({ type: 'mouse_position', x, y }));
  };

  const close = () => { if (ws.value) ws.value.close(); };

  return { ws, connectWebSocket, sendMousePosition, close };
}
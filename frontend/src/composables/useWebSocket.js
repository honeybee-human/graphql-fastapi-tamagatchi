import { ref } from 'vue';

export function useWebSocket(currentUser) {
  const ws = ref(null);
  let retry = 0;
  let shouldReconnect = true;
  let messageHandler = null;

  const setMessageHandler = (cb) => {
    messageHandler = typeof cb === 'function' ? cb : null;
    if (ws.value && messageHandler) {
      ws.value.onmessage = (evt) => {
        try {
          const data = JSON.parse(evt.data);
          messageHandler(data);
        } catch (_) {}
      };
    }
  };

  const openSocket = () => {
    if (!currentUser.value) return;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/${currentUser.value.id}`;
    ws.value = new WebSocket(wsUrl);
    ws.value.onopen = () => { retry = 0; };
    ws.value.onmessage = (evt) => {
      if (!messageHandler) return;
      try {
        const data = JSON.parse(evt.data);
        messageHandler(data);
      } catch (_) {}
    };
    ws.value.onclose = () => {
      if (!shouldReconnect) return;
      const delay = Math.min(30000, 1000 * Math.pow(2, retry));
      retry++;
      setTimeout(openSocket, delay);
    };
    ws.value.onerror = () => { try { ws.value.close(); } catch (_) {} };
  };

  const connectWebSocket = () => {
    shouldReconnect = true;
    openSocket();
  };

  const close = () => {
    shouldReconnect = false;
    if (ws.value) {
      try { ws.value.close(); } catch (_) {}
      ws.value = null;
    }
  };

  const sendMousePosition = (x, y) => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) return;
    ws.value.send(JSON.stringify({ type: 'mouse_position', x, y }));
  };

  const flushSave = () => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) return;
    try {
      ws.value.send(JSON.stringify({ type: 'flush_save' }));
    } catch (_) {}
  };

  return { ws, connectWebSocket, sendMousePosition, close, setMessageHandler, flushSave };
}
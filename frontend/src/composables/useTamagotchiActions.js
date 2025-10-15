import { useMutation } from '@vue/apollo-composable';
import { FEED_TAMAGOTCHI, PLAY_TAMAGOTCHI, SLEEP_TAMAGOTCHI, REVIVE_TAMAGOTCHI, RELEASE_TAMAGOTCHI, SUPPORT_TAMAGOTCHI } from '../graphql/tamagotchi';

export function useTamagotchiActions(allTamagotchisRef, pushToast) {
  const { mutate: feedMutation } = useMutation(FEED_TAMAGOTCHI);
  const { mutate: playMutation } = useMutation(PLAY_TAMAGOTCHI);
  const { mutate: sleepMutation } = useMutation(SLEEP_TAMAGOTCHI);
  const { mutate: reviveMutation } = useMutation(REVIVE_TAMAGOTCHI);
  const { mutate: releaseMutation } = useMutation(RELEASE_TAMAGOTCHI);
  const { mutate: supportMutation } = useMutation(SUPPORT_TAMAGOTCHI);

  const updateLocal = (u) => {
    if (!u) return;
    const list = allTamagotchisRef.value.map((t) => (t.id === u.id ? { ...t, ...u } : t));
    allTamagotchisRef.value = list;
  };

  const feedTamagotchi = async (target) => {
    if (!target) return;
    try { const res = await feedMutation({ id: target.id }); updateLocal(res?.data?.feedTamagotchi); pushToast?.(`you fed ${target.name}!`, 'success'); } catch { pushToast?.('failed to feed pet', 'error'); }
  };
  const playWithTamagotchi = async (target) => {
    if (!target) return;
    try { const res = await playMutation({ id: target.id }); updateLocal(res?.data?.playTamagotchi); pushToast?.(`you played with ${target.name}!`, 'success'); } catch { pushToast?.('failed to play with pet', 'error'); }
  };
  const sleepTamagotchi = async (target) => {
    if (!target) return;
    try { const res = await sleepMutation({ id: target.id }); updateLocal(res?.data?.sleepTamagotchi); pushToast?.(`you let ${target.name} rest.`, 'success'); } catch { pushToast?.('failed to rest pet', 'error'); }
  };
  const reviveTamagotchi = async (target) => {
    if (!target) return;
    try { const res = await reviveMutation({ id: target.id }); updateLocal(res?.data?.reviveTamagotchi); pushToast?.(`you revived ${target.name}!`, 'success'); } catch { pushToast?.('failed to revive pet', 'error'); }
  };
  const releaseTamagotchi = async (target) => {
    if (!target) return;
    try { const res = await releaseMutation({ id: target.id }); const ok = res?.data?.releaseTamagotchi; if (ok) { allTamagotchisRef.value = allTamagotchisRef.value.filter((t) => t.id !== target.id); pushToast?.(`you released ${target.name}.`, 'info'); } else { pushToast?.('failed to release pet', 'error'); } } catch { pushToast?.('failed to release pet', 'error'); }
  };
  const supportTamagotchi = async (target) => {
    if (!target) return;
    try { await supportMutation({ id: target.id }); pushToast?.(`you sent love to ${target.name}!`, 'success'); } catch { pushToast?.('failed to support pet', 'error'); }
  };

  return { feedTamagotchi, playWithTamagotchi, sleepTamagotchi, reviveTamagotchi, releaseTamagotchi, supportTamagotchi };
}
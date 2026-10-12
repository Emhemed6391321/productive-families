export const compressImageFile = (file: File, _max: number, _q: number): Promise<string> =>
  new Promise((res, rej) => { const r = new FileReader(); r.onloadend = () => res(r.result as string); r.onerror = rej; r.readAsDataURL(file); });

export function genRandomNum(n = 100000) {
  let num = `${Math.floor(Math.random() * n)}`;
  const len = `${n}`.length - 1;
  while (num.length < len) {
    num = `0${num}`;
  }
  return num;
}

export default function genUID(n = 100000) {
  return `${Date.now()}-${genRandomNum(n)}`;
}

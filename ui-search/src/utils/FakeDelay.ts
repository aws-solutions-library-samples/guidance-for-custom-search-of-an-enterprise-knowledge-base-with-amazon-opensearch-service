export default function fakeDelay(delay) {
  return new Promise((resolve) => setTimeout(resolve, delay));
}

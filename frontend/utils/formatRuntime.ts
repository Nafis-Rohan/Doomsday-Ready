/** 452 -> "7 h 32 min", 120 -> "2 h", 45 -> "45 min" */
export function formatRuntime(minutes: number): string {
  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60
  if (hours === 0) return `${rest} min`
  if (rest === 0) return `${hours} h`
  return `${hours} h ${rest} min`
}
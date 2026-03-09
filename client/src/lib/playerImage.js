export function playerImageUrl(player) {
  return player?.player_image_url || player?.image_url || '/player-fallback.svg'
}

export function onPlayerImageError(event) {
  event.currentTarget.src = '/player-fallback.svg'
}

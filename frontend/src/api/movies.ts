import type { Movie, MoviePatch, NewMovie, RewatchOrder } from '../types'
import { request } from './client'

export function listMovies() {
  return request<Movie[]>('GET', '/movies')
}

export function createMovie(movie: NewMovie) {
  return request<Movie>('POST', '/movies', movie)
}

export function updateMovie(id: number, changes: MoviePatch) {
  return request<Movie>('PATCH', `/movies/${id}`, changes)
}

export function getRewatchOrder(id: number) {
  return request<RewatchOrder>('GET', `/movies/${id}/rewatch-order`)
}
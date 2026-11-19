import type { BookingQuote, Cinema, NewCinema } from '../types'
import { request } from './client'

export function listCinemas() {
  return request<Cinema[]>('GET', '/cinemas')
}

export function createCinema(cinema: NewCinema) {
  return request<Cinema>('POST', '/cinemas', cinema)
}

export function getBookingQuote(cinemaId: number, groupSize: number) {
  return request<BookingQuote>(
    'GET',
    `/cinemas/${cinemaId}/booking?groupSize=${groupSize}`,
  )
}
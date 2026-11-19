export interface MovieRef {
  id: number
  title: string
}

export interface Movie {
  id: number
  title: string
  releaseYear: number
  runtimeMinutes: number
  watched: boolean
  prerequisites: MovieRef[]
  createdAt: string
  updatedAt: string
}

// A prerequisite can be given as a movie id or a movie title
export interface NewMovie {
  title: string
  releaseYear: number
  runtimeMinutes: number
  watched?: boolean
  prerequisites?: (number | string)[]
}

export type MoviePatch = Partial<NewMovie>

export interface RewatchMovie {
  id: number
  title: string
  releaseYear: number
  runtimeMinutes: number
  watched: boolean
}

export interface RewatchOrder {
  target: MovieRef
  order: RewatchMovie[]
  totalCount: number
  watchedCount: number
  unwatchedCount: number
  remainingRuntimeMinutes: number
}

export interface Cinema {
  id: number
  name: string
  bundleSizes: number[]
  createdAt: string
  updatedAt: string
}

export interface NewCinema {
  name: string
  bundleSizes: number[]
}

export interface BundleCount {
  size: number
  count: number
}

export interface BookingQuote {
  cinema: { id: number; name: string; bundleSizes: number[] }
  groupSize: number
  possible: boolean
  totalBundles: number | null
  bundles: BundleCount[]
  message?: string
}
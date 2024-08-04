import { writable } from 'svelte/store'
import { setContext, getContext } from 'svelte'

export function setAccordionOptions({ collapse }) {
	const activeComponentId = writable(null)
	setContext('collapse', collapse)
	setContext('activeComponentId', activeComponentId)
}

export function getAccordionOptions() {
	const collapse = getContext('collapse')
	const activeComponentId = getContext('activeComponentId')
	return { collapse, activeComponentId }
}

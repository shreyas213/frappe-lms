<template>
	<div class="max-w-5xl mx-auto px-5 py-6 space-y-6">
		<PageHeader :breadcrumbs="breadcrumbs" />

		<!-- Search Input Bar -->
		<div class="relative">
			<span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-[#A3A3A3]">
				<span class="lucide-search size-5" />
			</span>
			<input
				v-model="searchQuery"
				type="text"
				:placeholder="__('Search courses, lessons, batches, instructors, jobs, and certificates...')"
				class="w-full pl-12 pr-12 py-3.5 bg-[#1C1C1C] border border-[#333333] focus:border-[#FF6B00] rounded-xl text-white placeholder-[#777777] text-base outline-none transition-all shadow-sm"
				@input="onSearchInput"
			/>
			<button
				v-if="searchQuery"
				type="button"
				@click="clearSearch"
				class="absolute inset-y-0 right-0 pr-4 flex items-center text-[#A3A3A3] hover:text-white"
			>
				<span class="lucide-x size-4" />
			</button>
		</div>

		<!-- Category Filter Pills -->
		<div class="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
			<button
				v-for="cat in categories"
				:key="cat.value"
				type="button"
				@click="selectCategory(cat.value)"
				class="px-3.5 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all border flex items-center gap-1.5"
				:class="
					selectedCategory === cat.value
						? 'bg-[#FF6B00] text-white border-[#FF6B00] shadow-sm'
						: 'bg-[#1C1C1C] text-[#A3A3A3] hover:text-white border-[#333333] hover:border-[#555555]'
				"
			>
				<span>{{ cat.label }}</span>
				<span
					class="px-1.5 py-0.2 rounded-full text-[10px] font-bold"
					:class="selectedCategory === cat.value ? 'bg-black/30 text-white' : 'bg-[#262626] text-[#A3A3A3]'"
				>
					{{ counts[cat.value] ?? 0 }}
				</span>
			</button>
		</div>

		<!-- Loading State -->
		<div v-if="isSearching" class="flex items-center justify-center py-20 text-[#A3A3A3]">
			<LoadingIndicator class="size-6 text-[#FF6B00] mr-2" />
			<span class="text-sm">{{ __('Searching platform records...') }}</span>
		</div>

		<!-- Search Results List -->
		<div v-else-if="filteredResults.length" class="space-y-3">
			<div class="text-xs text-[#A3A3A3] font-medium">
				{{ __('Showing {0} results for "{1}"').format(filteredResults.length, searchQuery) }}
			</div>

			<div class="divide-y divide-[#333333] rounded-xl border border-[#333333] bg-[#1C1C1C] overflow-hidden shadow-sm">
				<router-link
					v-for="item in filteredResults"
					:key="item.type + item.id"
					:to="item.url"
					class="p-4 flex items-center justify-between gap-4 hover:bg-[#222222] transition-colors group block"
				>
					<div class="flex items-center gap-3.5 min-w-0">
						<!-- Icon / Thumbnail -->
						<div class="size-11 rounded-lg bg-[#262626] border border-[#333333] flex items-center justify-center shrink-0 overflow-hidden text-[#FF6B00]">
							<img
								v-if="item.image"
								:src="item.image"
								:alt="item.title"
								class="size-full object-cover"
							/>
							<span v-else-if="item.type === 'Courses'" class="lucide-book-open size-5" />
							<span v-else-if="item.type === 'Lessons'" class="lucide-play-circle size-5" />
							<span v-else-if="item.type === 'Batches'" class="lucide-users size-5" />
							<span v-else-if="item.type === 'Instructors'" class="lucide-user size-5" />
							<span v-else-if="item.type === 'Jobs'" class="lucide-briefcase size-5" />
							<span v-else-if="item.type === 'Certificates'" class="lucide-award size-5" />
							<span v-else class="lucide-file-text size-5" />
						</div>

						<div class="min-w-0 space-y-0.5">
							<div class="flex items-center gap-2">
								<span
									class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
									:class="getTypeBadgeClass(item.type)"
								>
									{{ item.badge || item.type }}
								</span>
								<h3 class="font-bold text-white text-sm group-hover:text-[#FF6B00] transition-colors truncate">
									{{ item.title }}
								</h3>
							</div>
							<p class="text-xs text-[#A3A3A3] truncate">
								{{ item.subtitle }}
							</p>
						</div>
					</div>

					<span class="lucide-arrow-right size-4 text-[#777777] group-hover:text-[#FF6B00] group-hover:translate-x-1 transition-all shrink-0" />
				</router-link>
			</div>
		</div>

		<!-- Empty State: No results -->
		<div v-else-if="searchQuery" class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-12 text-center max-w-lg mx-auto space-y-4">
			<div class="size-14 rounded-full bg-[#FF6B00]/15 text-[#FF6B00] border border-[#FF6B00]/30 flex items-center justify-center mx-auto">
				<span class="lucide-search-x size-7" />
			</div>
			<h3 class="text-lg font-bold text-white">
				{{ __('No results found for "{0}"').format(searchQuery) }}
			</h3>
			<p class="text-xs text-[#A3A3A3]">
				{{ __('Try checking your spelling, using broader terms, or switching between category tabs.') }}
			</p>
			<div class="pt-2 flex items-center justify-center gap-2">
				<router-link
					:to="{ name: 'Courses' }"
					class="px-4 py-2 rounded-lg text-xs font-semibold bg-[#FF6B00] hover:bg-[#FF8C00] text-white transition-colors"
				>
					{{ __('Browse All Courses') }}
				</router-link>
			</div>
		</div>

		<!-- Initial State: Prompt to search -->
		<div v-else class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-12 text-center max-w-lg mx-auto space-y-4">
			<div class="size-14 rounded-full bg-[#FF6B00]/15 text-[#FF6B00] border border-[#FF6B00]/30 flex items-center justify-center mx-auto">
				<span class="lucide-search size-7" />
			</div>
			<h3 class="text-lg font-bold text-white">
				{{ __('Search Learning Platform') }}
			</h3>
			<p class="text-xs text-[#A3A3A3]">
				{{ __('Type a keyword above to instantly search across courses, lessons, batches, instructors, job openings, and certificates.') }}
			</p>
		</div>
	</div>
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { call, LoadingIndicator, usePageMeta } from 'frappe-ui'
import PageHeader from '@/components/Layouts/PageHeader.vue'

const route = useRoute()
const router = useRouter()

const searchQuery = ref('')
const selectedCategory = ref('All')
const isSearching = ref(false)
const searchResults = ref([])
const counts = ref({
	All: 0,
	Courses: 0,
	Lessons: 0,
	Batches: 0,
	Instructors: 0,
	Jobs: 0,
	Certificates: 0,
})

let debounceTimer = null

const categories = [
	{ label: __('All'), value: 'All' },
	{ label: __('Courses'), value: 'Courses' },
	{ label: __('Lessons'), value: 'Lessons' },
	{ label: __('Batches'), value: 'Batches' },
	{ label: __('Instructors'), value: 'Instructors' },
	{ label: __('Jobs'), value: 'Jobs' },
	{ label: __('Certifications'), value: 'Certificates' },
]

const breadcrumbs = computed(() => [
	{ label: __('Search'), route: { name: 'SearchResults' } },
])

const onSearchInput = () => {
	clearTimeout(debounceTimer)
	debounceTimer = setTimeout(() => {
		executeSearch()
	}, 250)
}

const clearSearch = () => {
	searchQuery.value = ''
	searchResults.value = []
	counts.value = {
		All: 0,
		Courses: 0,
		Lessons: 0,
		Batches: 0,
		Instructors: 0,
		Jobs: 0,
		Certificates: 0,
	}
	router.replace({ query: {} })
}

const selectCategory = (cat) => {
	selectedCategory.value = cat
}

const executeSearch = () => {
	const q = searchQuery.value.trim()
	if (!q) {
		searchResults.value = []
		return
	}

	isSearching.value = true
	router.replace({ query: { q } })

	call('lms.lms.api.global_search', {
		query: q,
		category: 'All',
	})
		.then((res) => {
			if (res) {
				searchResults.value = res.results || []
				counts.value = res.counts || counts.value
			}
		})
		.catch(() => {
			searchResults.value = []
		})
		.finally(() => {
			isSearching.value = false
		})
}

const filteredResults = computed(() => {
	if (selectedCategory.value === 'All') {
		return searchResults.value
	}
	return searchResults.value.filter(
		(r) => r.type === selectedCategory.value
	)
})

const getTypeBadgeClass = (type) => {
	switch (type) {
		case 'Courses':
			return 'bg-[#FF6B00]/15 text-[#FF8C00] border border-[#FF6B00]/30'
		case 'Lessons':
			return 'bg-blue-500/15 text-blue-400 border border-blue-500/30'
		case 'Batches':
			return 'bg-purple-500/15 text-purple-400 border border-purple-500/30'
		case 'Instructors':
			return 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
		case 'Jobs':
			return 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
		case 'Certificates':
			return 'bg-green-500/15 text-green-400 border border-green-500/30'
		default:
			return 'bg-[#333333] text-white'
	}
}

onMounted(() => {
	const queryParam = route.query.q
	if (queryParam) {
		searchQuery.value = queryParam
		executeSearch()
	}
})

usePageMeta(() => ({
	title: __('Global Search'),
}))
</script>

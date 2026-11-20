<template>
	<div class="space-y-6 pb-12">
		<!-- Top Bar: Navigation & Mode Switcher -->
		<div class="px-5 pt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
			<PageHeader :breadcrumbs="breadcrumbs" />

			<div class="flex items-center gap-3">
				<TabButtons
					v-if="user.data"
					v-model="activeSection"
					:options="sectionTabs"
					class="w-fit shrink-0"
				/>

				<Button :route="{ name: 'Courses', query: { certification: true } }">
					<template #prefix>
						<span class="lucide-graduation-cap size-4" />
					</template>
					{{ __('Get Certified') }}
				</Button>
			</div>
		</div>

		<!-- SECTION 1: MY CERTIFICATES (Default for student) -->
		<div v-if="activeSection === 'my_certificates'" class="px-5 space-y-6">
			<!-- Banner / Header -->
			<div class="rounded-2xl bg-gradient-to-r from-[#1C1C1C] via-[#241711] to-[#1C1C1C] border border-[#FF6B00]/30 p-6 text-white shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div class="space-y-1">
					<div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-[#FF6B00]/20 text-[#FF8C00] border border-[#FF6B00]/40">
						<span class="lucide-award size-3.5" />
						<span>{{ __('Verified Credentials') }}</span>
					</div>
					<h1 class="text-2xl font-extrabold text-white">
						{{ __('My Official Certifications') }}
					</h1>
					<p class="text-xs md:text-sm text-[#A3A3A3]">
						{{ __('Official certificates earned by completing 100% of course curriculum and requirements.') }}
					</p>
				</div>

				<div class="flex items-center gap-4 bg-[#111111]/80 rounded-xl p-3 border border-[#333333]">
					<div class="text-center px-2">
						<div class="text-2xl font-black text-[#FF6B00]">
							{{ myCertificates.data?.length || 0 }}
						</div>
						<div class="text-[11px] text-[#A3A3A3] font-medium uppercase tracking-wider">
							{{ __('Earned') }}
						</div>
					</div>
				</div>
			</div>

			<!-- Loading State -->
			<div v-if="myCertificates.loading && !myCertificates.data" class="flex items-center justify-center py-20 text-[#A3A3A3]">
				<LoadingIndicator class="size-6 text-[#FF6B00] mr-2" />
				<span class="text-sm">{{ __('Loading your certificates...') }}</span>
			</div>

			<!-- Certificates Grid -->
			<div v-else-if="myCertificates.data?.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
				<div
					v-for="cert in myCertificates.data"
					:key="cert.name"
					class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-5 shadow-sm hover:border-[#FF6B00]/50 transition-all flex flex-col justify-between space-y-4 group"
				>
					<div class="space-y-3">
						<!-- Card Top -->
						<div class="flex items-start justify-between gap-3">
							<div class="size-12 rounded-xl bg-[#FF6B00]/15 text-[#FF6B00] border border-[#FF6B00]/30 flex items-center justify-center shrink-0">
								<span class="lucide-award size-6" />
							</div>

							<div class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#22C55E]/15 text-[#22C55E] border border-[#22C55E]/30">
								<span class="lucide-check-circle size-3" />
								<span>{{ __('Verified') }}</span>
							</div>
						</div>

						<!-- Course Title & ID -->
						<div>
							<h3 class="font-bold text-white text-base group-hover:text-[#FF6B00] transition-colors line-clamp-2">
								{{ cert.course_title || cert.batch_title || __('Course Certificate') }}
							</h3>
							<div class="text-xs font-mono text-[#FF8C00] mt-1">
								ID: {{ cert.name }}
							</div>
						</div>

						<div class="text-xs text-[#A3A3A3] flex items-center gap-2">
							<span class="lucide-calendar size-3.5" />
							<span>{{ __('Issued on:') }} {{ dayjs(cert.issue_date).format('DD MMMM YYYY') }}</span>
						</div>
					</div>

					<!-- Card Action Buttons -->
					<div class="pt-3 border-t border-[#333333] flex items-center justify-between gap-2">
						<button
							type="button"
							@click="openPreview(cert)"
							class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#262626] hover:bg-[#333333] text-white transition-colors inline-flex items-center gap-1.5"
						>
							<span class="lucide-eye size-3.5" />
							<span>{{ __('Preview') }}</span>
						</button>

						<div class="flex items-center gap-1.5">
							<a
								:href="`/api/method/frappe.utils.print_format.download_pdf?doctype=LMS+Certificate&name=${cert.name}&format=${cert.template || 'Certificate'}&no_letterhead=1`"
								target="_blank"
								class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#FF6B00] hover:bg-[#FF8C00] text-white transition-colors inline-flex items-center gap-1.5 shadow-sm"
								:title="__('Download official PDF')"
							>
								<span class="lucide-download size-3.5" />
								<span>{{ __('PDF') }}</span>
							</a>

							<a
								:href="`/certificate?certificate_id=${cert.name}`"
								target="_blank"
								class="p-1.5 rounded-lg text-xs font-semibold bg-[#262626] hover:bg-[#333333] text-[#A3A3A3] hover:text-white transition-colors"
								:title="__('Public verification link')"
							>
								<span class="lucide-external-link size-3.5" />
							</a>
						</div>
					</div>
				</div>
			</div>

			<!-- Empty State when 0 certificates -->
			<div v-else class="rounded-2xl border border-[#333333] bg-[#1C1C1C] p-12 text-center max-w-xl mx-auto space-y-4">
				<div class="size-16 rounded-full bg-[#FF6B00]/15 text-[#FF6B00] border border-[#FF6B00]/30 flex items-center justify-center mx-auto">
					<span class="lucide-graduation-cap size-8" />
				</div>
				<h3 class="text-xl font-bold text-white">
					{{ __('No Certificates Earned Yet') }}
				</h3>
				<p class="text-xs md:text-sm text-[#A3A3A3] max-w-md mx-auto">
					{{ __('Complete 100% of the lessons and mandatory requirements in any certified course to automatically receive your verified digital certificate.') }}
				</p>
				<div class="pt-2">
					<Button
						variant="solid"
						:route="{ name: 'Courses', query: { certification: true } }"
					>
						<template #prefix>
							<span class="lucide-book-open size-4" />
						</template>
						{{ __('Explore Certified Courses') }}
					</Button>
				</div>
			</div>
		</div>

		<!-- SECTION 2: CERTIFIED MEMBERS DIRECTORY -->
		<div v-show="activeSection === 'directory'">
			<ListPage
				:breadcrumbs="breadcrumbs"
				:rows="rows"
				:total-count="memberCount"
				:loading="participants.list.loading"
				:has-next-page="participants.hasNextPage"
				row-key="key"
				v-model:page-length="pageLength"
				empty-name="Certified Members"
				empty-icon="lucide-badge-check"
				:empty-title="emptyState?.title"
				:empty-description="emptyState?.description"
				@load-more="participants.next()"
			>
				<template v-if="emptyState" #empty-actions>
					<EmptyStateActions
						list="certified_participants"
						:create-label="__('New Course')"
						docs="https://docs.frappe.io/learning/issue-a-certificate"
						@create="newCourseFromEmptyState"
					/>
				</template>

				<template #actions>
					<Button :route="{ name: 'Courses', query: { certification: true } }">
						<template #prefix>
							<span class="lucide-graduation-cap size-4" />
						</template>
						{{ __('Get Certified') }}
					</Button>
				</template>

				<template #name> {{ memberCount }} {{ __('Certified Members') }} </template>

				<template #filters>
					<FormControl
						v-model="nameFilter"
						:placeholder="__('Search')"
						:aria-label="__('Search')"
						type="text"
					>
						<template #prefix>
							<span class="lucide-search size-4 text-ink-gray-5" />
						</template>
					</FormControl>
					<ClearableCombobox
						v-if="categories.data?.length"
						v-model="currentCategory"
						:options="categories.data.filter((c) => c.value)"
						:placeholder="__('Category')"
						@update:modelValue="updateParticipants()"
					/>
					<ToggleFilter
						:modelValue="openToWork"
						:label="__('Open to Work')"
						@update:modelValue="setOpenToWork"
					/>
					<ToggleFilter
						:modelValue="hiring"
						:label="__('Hiring')"
						@update:modelValue="setHiring"
					/>
				</template>

				<template #card="{ row }">
					<component
						:is="row.username ? 'router-link' : 'div'"
						:to="profileRoute(row.username, 'ProfileAbout')"
						class="flex flex-col rounded-6 border p-3 text-ink-gray-9"
						:class="
							row.username ? 'cursor-pointer hover:border-outline-gray-3' : ''
						"
					>
						<div class="flex items-center gap-x-4">
							<UserAvatar :user="row" size="2xl" />
							<div class="flex flex-col">
								<div class="line-clamp-1 font-semibold">
									{{ row.full_name }}
								</div>
								<div class="mb-4 line-clamp-1 text-sm leading-5">
									{{
										row.headline || 'Joined ' + serverTime(row.creation).fromNow()
									}}
								</div>
							</div>
						</div>
						<div class="mt-auto space-y-2 text-ink-gray-7">
							<div>
								<Badge size="lg">
									<template #prefix>
										<span class="lucide-graduation-cap size-3" />
									</template>
									{{ row.certificate_count }}
									{{
										row.certificate_count > 1
											? __('certificates')
											: __('certificate')
									}}
								</Badge>
							</div>
							<div class="flex items-center gap-x-1">
								<span class="lucide-calendar me-1 h-4 w-4" />
								<span>{{ dayjs(row.issue_date).format('DD MMM YYYY') }}</span>
							</div>
						</div>
					</component>
				</template>
			</ListPage>
		</div>

		<!-- PREVIEW CERTIFICATE MODAL -->
		<Dialog
			v-model="showPreviewModal"
			:options="{
				title: __('Official Certificate Preview'),
				size: '2xl',
			}"
		>
			<template #body-content>
				<div v-if="previewCert" class="space-y-4">
					<!-- Certificate Frame -->
					<div class="rounded-xl border-2 border-[#D4AF37] bg-gradient-to-b from-[#1E1E1E] to-[#121212] p-8 text-center shadow-2xl relative overflow-hidden">
						<div class="border border-dashed border-[#D4AF37]/50 p-6 rounded-lg">
							<div class="size-16 rounded-full bg-[#FF6B00]/20 text-[#FF8C00] border border-[#FF6B00]/40 flex items-center justify-center mx-auto mb-3">
								<span class="lucide-award size-8" />
							</div>
							<div class="text-xs uppercase tracking-widest text-[#D4AF37] font-bold mb-1">
								{{ __('Certificate of Completion') }}
							</div>
							<div class="text-xs text-[#A3A3A3] mb-2">{{ __('This certifies that') }}</div>
							<div class="text-2xl font-black text-white mb-2 underline decoration-[#FF6B00]/40 underline-offset-4">
								{{ user.data?.full_name || __('Student') }}
							</div>
							<div class="text-xs text-[#A3A3A3] mb-1">{{ __('has successfully completed the course') }}</div>
							<div class="text-lg font-bold text-[#FF8C00] mb-4">
								{{ previewCert.course_title || previewCert.batch_title }}
							</div>

							<div class="grid grid-cols-2 gap-4 pt-4 border-t border-[#333333] text-left text-xs">
								<div>
									<div class="text-[#A3A3A3] uppercase text-[10px]">{{ __('Certificate ID') }}</div>
									<div class="font-mono text-white">{{ previewCert.name }}</div>
								</div>
								<div>
									<div class="text-[#A3A3A3] uppercase text-[10px]">{{ __('Date Issued') }}</div>
									<div class="text-white">{{ dayjs(previewCert.issue_date).format('DD MMMM YYYY') }}</div>
								</div>
							</div>
						</div>
					</div>

					<div class="flex items-center justify-end gap-3 pt-2">
						<a
							:href="`/api/method/frappe.utils.print_format.download_pdf?doctype=LMS+Certificate&name=${previewCert.name}&format=${previewCert.template || 'Certificate'}&no_letterhead=1`"
							target="_blank"
							class="px-4 py-2 rounded-lg text-xs font-semibold bg-[#FF6B00] hover:bg-[#FF8C00] text-white transition-colors inline-flex items-center gap-1.5 shadow"
						>
							<span class="lucide-download size-4" />
							<span>{{ __('Download PDF') }}</span>
						</a>

						<a
							:href="`/certificate?certificate_id=${previewCert.name}`"
							target="_blank"
							class="px-4 py-2 rounded-lg text-xs font-semibold bg-[#262626] hover:bg-[#333333] text-white transition-colors inline-flex items-center gap-1.5 border border-[#333333]"
						>
							<span class="lucide-shield-check size-4 text-[#22C55E]" />
							<span>{{ __('Public Verification Page') }}</span>
						</a>
					</div>
				</div>
			</template>
		</Dialog>
	</div>
</template>

<script setup>
import {
	Badge,
	Button,
	call,
	createListResource,
	createResource,
	Dialog,
	FormControl,
	LoadingIndicator,
	TabButtons,
	usePageMeta,
} from 'frappe-ui'
import ClearableCombobox from '@/components/Controls/ClearableCombobox.vue'
import ToggleFilter from '@/components/Controls/ToggleFilter.vue'
import { computed, inject, onMounted, ref, watch } from 'vue'
import { sessionStore } from '../stores/session'
import { useRouter } from 'vue-router'
import { openFormRoute } from '@/composables/useFormRoute'
import { setFormSource } from '@/composables/formTracking'
import UserAvatar from '@/components/UserAvatar.vue'
import ListPage from '@/components/Layouts/ListPage.vue'
import PageHeader from '@/components/Layouts/PageHeader.vue'
import EmptyStateActions from '@/components/EmptyStateActions.vue'
import { profileRoute } from '@/utils/routes'
import { serverTime } from '@/utils/dayjs'

const filters = ref({})
const currentCategory = ref('')
const nameFilter = ref('')
const openToWork = ref(false)
const hiring = ref(false)
const { brand } = sessionStore()
const memberCount = ref(0)
const dayjs = inject('$dayjs')
const user = inject('$user')
const router = useRouter()

const activeSection = ref(user.data ? 'my_certificates' : 'directory')
const sectionTabs = [
	{ label: __('My Certificates'), value: 'my_certificates' },
	{ label: __('Certified Directory'), value: 'directory' },
]

const showPreviewModal = ref(false)
const previewCert = ref(null)

const openPreview = (cert) => {
	previewCert.value = cert
	showPreviewModal.value = true
}

const myCertificates = createResource({
	url: 'frappe.client.get_list',
	makeParams() {
		return {
			doctype: 'LMS Certificate',
			filters: { member: user.data?.name },
			fields: ['name', 'course', 'course_title', 'batch_name', 'batch_title', 'issue_date', 'template', 'published'],
			order_by: 'issue_date desc, creation desc',
			limit_page_length: 50,
		}
	},
	auto: Boolean(user.data?.name),
})

const emptyState = computed(() => {
	if (window.read_only_mode) return null
	if (!user.data?.is_instructor && !user.data?.is_moderator) return null
	return {
		title: __('No one is certified yet'),
		description: __(
			'Learners who finish a course with a certificate show up here. Add one to a course to begin.'
		),
	}
})

function newCourseFromEmptyState() {
	setFormSource('empty_state')
	openFormRoute(router, { name: 'NewCourse' })
}

onMounted(() => {
	if (!user.data) {
		activeSection.value = 'directory'
	} else {
		myCertificates.reload()
	}
	setFiltersFromQuery()
	updateParticipants()
	watch(nameFilter, () => updateParticipants())
})

const participants = createListResource({
	doctype: 'LMS Certificate',
	url: 'lms.lms.api.get_certified_participants',
	start: 0,
	pageLength: 24,
	cache: ['certified_participants'],
})

const categories = createResource({
	url: 'lms.lms.api.get_categories',
	cache: 'categories',
	auto: true,
})

const pageLength = ref(24)

const rows = computed(() => {
	if (!participants.data) return []
	return participants.data.map((participant) => ({
		...participant,
		key: participant.username || participant.full_name,
	}))
})

const updateParticipants = () => {
	let currentFilters = {}
	if (currentCategory.value) {
		currentFilters.category = currentCategory.value
	}
	if (openToWork.value) {
		currentFilters.open_to = 'Work'
	}
	if (hiring.value) {
		currentFilters.open_to = 'Hiring'
	}
	if (nameFilter.value) {
		currentFilters.name = nameFilter.value
	}
	filters.value = currentFilters
	setQueryParams(currentFilters)

	participants.update({
		filters: currentFilters,
	})
	participants.reload()

	call('lms.lms.api.get_certified_participants_count', {
		filters: currentFilters,
	}).then((data) => {
		memberCount.value = data
	})
}

const setOpenToWork = (value) => {
	openToWork.value = value
	if (value) hiring.value = false
	updateParticipants()
}

const setHiring = (value) => {
	hiring.value = value
	if (value) openToWork.value = false
	updateParticipants()
}

const setQueryParams = (filters) => {
	let filterKeys = {
		name: filters.name,
		category: filters.category,
		'open-to-work': filters.open_to === 'Work',
		hiring: filters.open_to === 'Hiring',
	}
	let queries = new URLSearchParams(location.search)
	Object.keys(filterKeys).forEach((key) => {
		if (hasValue(filterKeys[key])) {
			queries.set(key, filterKeys[key])
		} else {
			queries.delete(key)
		}
	})
	history.replaceState(
		{},
		'',
		`${location.pathname}${queries.size > 0 ? `?${queries.toString()}` : ''}`
	)
}

const hasValue = (value) => {
	if (typeof value === 'string') {
		return value.trim() !== ''
	}
	return true
}

const setFiltersFromQuery = () => {
	let queries = new URLSearchParams(location.search)
	nameFilter.value = queries.get('name') || ''
	currentCategory.value = queries.get('category') || ''
	openToWork.value = queries.get('open-to-work') === 'true'
	hiring.value = queries.get('hiring') === 'true'
}

const breadcrumbs = computed(() => [
	{
		label: __('Certifications'),
		route: { name: 'CertifiedParticipants' },
	},
])

usePageMeta(() => {
	return {
		title: __('Certifications'),
		icon: brand.favicon,
	}
})
</script>

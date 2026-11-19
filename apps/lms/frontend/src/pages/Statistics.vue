<template>
	<div class="space-y-6 pb-12">
		<!-- Top Controls Bar -->
		<div class="flex flex-col md:flex-row md:items-center justify-between gap-4 px-5 pt-4">
			<PageHeader :breadcrumbs="breadcrumbs" />

			<div class="flex items-center gap-2.5 flex-wrap">
				<!-- Date Range Filter -->
				<select
					v-model="selectedDateRange"
					@change="onDateRangeChange"
					class="bg-[#1C1C1C] border border-[#333333] text-white text-xs font-semibold rounded-lg px-3 py-2 outline-none focus:border-[#FF6B00] transition-colors"
				>
					<option value="all">{{ __('All Time') }}</option>
					<option value="30_days">{{ __('Last 30 Days') }}</option>
					<option value="7_days">{{ __('Last 7 Days') }}</option>
				</select>

				<!-- Refresh Button -->
				<button
					type="button"
					@click="refreshStatistics"
					:disabled="isRefreshing"
					class="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-[#1C1C1C] hover:bg-[#262626] border border-[#333333] text-xs font-semibold text-white transition-colors"
					:title="__('Reload metrics and charts')"
				>
					<span class="lucide-refresh-cw size-3.5" :class="{ 'animate-spin': isRefreshing }" />
					<span>{{ __('Refresh') }}</span>
				</button>

				<!-- Reset LMS Statistics Button (Administrative only) -->
				<button
					v-if="isSystemManager"
					type="button"
					@click="openResetModal"
					class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-[#FF6B00]/15 hover:bg-[#FF6B00]/25 text-[#FF6B00] border border-[#FF6B00]/40 text-xs font-bold transition-all shadow-sm"
				>
					<span class="lucide-rotate-ccw size-3.5" />
					<span>{{ __('Reset LMS Statistics') }}</span>
				</button>
			</div>
		</div>

		<!-- Reset Cutoff Notice Banner -->
		<div
			v-if="chartDetails.data?.analytics_reset_timestamp"
			class="mx-5 p-3.5 rounded-xl border border-[#FF6B00]/30 bg-[#FF6B00]/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-white"
		>
			<div class="flex items-center gap-2">
				<span class="lucide-info size-4 text-[#FF8C00] shrink-0" />
				<span>
					{{ __('LMS Analytics reset is active (since {0}). Displayed metrics reflect activity after this cutoff. Real student and course data remain safe.').format(chartDetails.data.analytics_reset_timestamp) }}
				</span>
			</div>
			<button
				v-if="isSystemManager"
				type="button"
				@click="restoreHistoricalAnalytics"
				class="px-3 py-1 rounded bg-[#FF6B00] hover:bg-[#FF8C00] text-white font-semibold shrink-0 transition-colors self-start sm:self-auto"
			>
				{{ __('Restore Full History') }}
			</button>
		</div>

		<!-- Loading state -->
		<div
			v-if="chartDetails.loading && !chartDetails.data"
			class="flex flex-1 items-center justify-center py-20 text-[#A3A3A3]"
		>
			<LoadingIndicator class="size-6 text-[#FF6B00] mr-2" />
			<span class="text-sm">{{ __('Loading LMS metrics...') }}</span>
		</div>

		<!-- Main Statistics Content -->
		<div v-else-if="chartDetails.data" class="px-5 space-y-6">
			<!-- Metrics KPI Cards -->
			<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
				<!-- Courses -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF6B00]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Courses') }}</span>
						<div class="p-2 rounded-lg bg-[#FF6B00]/15 text-[#FF6B00]">
							<span class="lucide-book-open size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ compactNumber(chartDetails.data.courses) }}
					</div>
					<div class="text-xs text-[#A3A3A3] mt-1">
						{{ __('Published courses') }}
					</div>
				</div>

				<!-- Signups -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF6B00]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Signups') }}</span>
						<div class="p-2 rounded-lg bg-[#FF8C00]/15 text-[#FF8C00]">
							<span class="lucide-users size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ compactNumber(chartDetails.data.users) }}
					</div>
					<div class="text-xs text-[#A3A3A3] mt-1">
						{{ __('Active learners') }}
					</div>
				</div>

				<!-- Enrollments -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF6B00]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Enrollments') }}</span>
						<div class="p-2 rounded-lg bg-[#FF6B00]/15 text-[#FF6B00]">
							<span class="lucide-graduation-cap size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ compactNumber(chartDetails.data.enrollments) }}
					</div>
					<div class="text-xs text-[#A3A3A3] mt-1">
						{{ __('Course enrollments') }}
					</div>
				</div>

				<!-- Completions -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#22C55E]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Completions') }}</span>
						<div class="p-2 rounded-lg bg-[#22C55E]/15 text-[#22C55E]">
							<span class="lucide-check-circle size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ compactNumber(chartDetails.data.completions) }}
					</div>
					<div class="text-xs text-[#A3A3A3] mt-1">
						{{ __('Course completions') }}
					</div>
				</div>

				<!-- Certifications -->
				<div class="col-span-2 md:col-span-1 rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF8C00]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Certificates') }}</span>
						<div class="p-2 rounded-lg bg-[#FF8C00]/15 text-[#FF8C00]">
							<span class="lucide-award size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ compactNumber(chartDetails.data.certifications) }}
					</div>
					<div class="text-xs text-[#A3A3A3] mt-1">
						{{ __('Issued credentials') }}
					</div>
				</div>
			</div>

			<!-- Trends Charts Grid -->
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
				<!-- Signups Trend -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm h-72 flex flex-col">
					<div class="flex items-center justify-between mb-2">
						<h3 class="text-sm font-bold text-white flex items-center gap-2">
							<span class="lucide-user-plus size-4 text-[#FF6B00]" />
							<span>{{ __('Signups Trend') }}</span>
						</h3>
						<span class="text-xs text-[#A3A3A3]">{{ __('New accounts per day') }}</span>
					</div>
					<div class="flex-1 min-h-0">
						<LineChart
							v-if="hasPoints(signupsChart.data)"
							:data="signupsChart.data"
							x="date"
							y="count"
							title="Signups"
							subtitle="Signups per day"
							:x-axis="{ type: 'time', timeGrain: 'day' }"
						/>
						<ChartEmptyState
							v-else
							:title="__('Signups')"
							:subtitle="__('Signups per day')"
							:message="__('New accounts on your site show up here, day by day, as people join.')"
							icon="lucide-user-plus"
						/>
					</div>
				</div>

				<!-- Enrollments Trend -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm h-72 flex flex-col">
					<div class="flex items-center justify-between mb-2">
						<h3 class="text-sm font-bold text-white flex items-center gap-2">
							<span class="lucide-book-open size-4 text-[#FF8C00]" />
							<span>{{ __('Enrollments Trend') }}</span>
						</h3>
						<span class="text-xs text-[#A3A3A3]">{{ __('Enrollments per day') }}</span>
					</div>
					<div class="flex-1 min-h-0">
						<LineChart
							v-if="hasPoints(enrollmentChart.data)"
							:data="enrollmentChart.data"
							x="date"
							y="count"
							title="Enrollments"
							subtitle="Enrollments per day"
							:x-axis="{ type: 'time', timeGrain: 'day' }"
						/>
						<ChartEmptyState
							v-else
							:title="__('Enrollments')"
							:subtitle="__('Enrollments per day')"
							:message="__('Each time a learner joins one of your courses, it shows up here.')"
							icon="lucide-book-open"
						/>
					</div>
				</div>

				<!-- Certifications Trend -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm h-72 flex flex-col">
					<div class="flex items-center justify-between mb-2">
						<h3 class="text-sm font-bold text-white flex items-center gap-2">
							<span class="lucide-award size-4 text-[#FF6B00]" />
							<span>{{ __('Certifications Trend') }}</span>
						</h3>
						<span class="text-xs text-[#A3A3A3]">{{ __('Certificates per day') }}</span>
					</div>
					<div class="flex-1 min-h-0">
						<LineChart
							v-if="hasPoints(certification.data)"
							:data="certification.data"
							x="date"
							y="count"
							title="Certifications"
							subtitle="Certifications per day"
							:x-axis="{ type: 'time', timeGrain: 'day' }"
						/>
						<ChartEmptyState
							v-else
							:title="__('Certifications')"
							:subtitle="__('Certifications per day')"
							:message="__('Certificates your learners earn show up here, day by day.')"
							icon="lucide-badge-check"
						/>
					</div>
				</div>

				<!-- Course Completion Donut -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm h-72 flex flex-col">
					<div class="flex items-center justify-between mb-2">
						<h3 class="text-sm font-bold text-white flex items-center gap-2">
							<span class="lucide-circle-check size-4 text-[#22C55E]" />
							<span>{{ __('Course Completion Ratio') }}</span>
						</h3>
						<span class="text-xs text-[#A3A3A3]">{{ __('Completed vs In Progress') }}</span>
					</div>
					<div class="flex-1 min-h-0">
						<DonutChart
							v-if="hasCompletions"
							:data="courseCompletion.data"
							category="label"
							value="value"
							title="Completions"
							subtitle="Course Completion"
							:center-label="__('Enrollments')"
						/>
						<ChartEmptyState
							v-else
							:title="__('Completions')"
							:subtitle="__('Course Completion')"
							:message="__('When learners finish a course, you will see how many completed out of everyone enrolled.')"
							icon="lucide-circle-check"
						/>
					</div>
				</div>
			</div>
		</div>

		<!-- Reset Statistics Confirmation Modal -->
		<div
			v-if="showResetModal"
			class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
			@click.self="closeResetModal"
		>
			<div class="w-full max-w-2xl bg-[#1C1C1C] border border-[#333333] rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
				<!-- Modal Header -->
				<div class="p-5 border-b border-[#333333] flex items-center justify-between bg-[#111111]">
					<div class="flex items-center gap-3">
						<div class="p-2 rounded-xl bg-[#FF6B00]/15 text-[#FF6B00] border border-[#FF6B00]/30">
							<span class="lucide-shield-alert size-5" />
						</div>
						<div>
							<h3 class="text-lg font-bold text-white">
								{{ __('Reset LMS Statistics & Data Management') }}
							</h3>
							<p class="text-xs text-[#A3A3A3]">
								{{ __('Choose the administrative operation you want to perform') }}
							</p>
						</div>
					</div>
					<button
						type="button"
						@click="closeResetModal"
						class="text-[#A3A3A3] hover:text-white p-1 rounded-lg transition-colors"
					>
						<span class="lucide-x size-5" />
					</button>
				</div>

				<!-- Modal Tabs -->
				<div class="flex border-b border-[#333333] bg-[#161616]">
					<button
						type="button"
						@click="activeResetTab = 'analytics'"
						:class="activeResetTab === 'analytics' ? 'border-b-2 border-[#FF6B00] text-white bg-[#1C1C1C]' : 'text-[#A3A3A3] hover:text-white'"
						class="flex-1 py-3 px-4 text-xs font-bold transition-all flex items-center justify-center gap-2"
					>
						<span class="lucide-bar-chart size-4 text-[#FF6B00]" />
						<span>{{ __('Option A: Reset Analytics Counters') }}</span>
					</button>
					<button
						type="button"
						@click="activeResetTab = 'demo'"
						:class="activeResetTab === 'demo' ? 'border-b-2 border-[#EF4444] text-white bg-[#1C1C1C]' : 'text-[#A3A3A3] hover:text-white'"
						class="flex-1 py-3 px-4 text-xs font-bold transition-all flex items-center justify-center gap-2"
					>
						<span class="lucide-trash-2 size-4 text-[#EF4444]" />
						<span>{{ __('Option B: Delete Demo Data') }}</span>
					</button>
				</div>

				<!-- Modal Body -->
				<div class="p-6 overflow-y-auto space-y-6">
					<!-- Feedback message -->
					<div
						v-if="modalMessage"
						class="p-3.5 rounded-xl border text-xs flex items-center gap-2"
						:class="modalMessage.isError ? 'bg-[#EF4444]/15 border-[#EF4444] text-red-200' : 'bg-[#22C55E]/15 border-[#22C55E] text-green-200'"
					>
						<span :class="modalMessage.isError ? 'lucide-alert-circle text-[#EF4444]' : 'lucide-check-circle text-[#22C55E]'" class="size-4 shrink-0" />
						<span>{{ modalMessage.text }}</span>
					</div>

					<!-- Option A: Reset Analytics -->
					<div v-if="activeResetTab === 'analytics'" class="space-y-4">
						<div class="p-4 rounded-xl border border-[#333333] bg-[#111111] space-y-2">
							<h4 class="text-sm font-bold text-white flex items-center gap-2">
								<span class="lucide-info size-4 text-[#FF6B00]" />
								<span>{{ __('What will Option A do?') }}</span>
							</h4>
							<ul class="text-xs text-[#A3A3A3] space-y-1.5 list-disc pl-5">
								<li>{{ __('Resets displayed statistics (signups, enrollments, completions, certifications) to 0.') }}</li>
								<li>{{ __('Sets an analytics reporting cutoff timestamp to the current moment.') }}</li>
								<li><strong class="text-white">{{ __('Strictly preserves') }}</strong> {{ __('all real student accounts, course content, progress records, and certificates.') }}</li>
								<li><strong class="text-white">{{ __('No accounts or database rows') }}</strong> {{ __('are deleted.') }}</li>
							</ul>
						</div>

						<div class="space-y-3 pt-2">
							<label class="flex items-start gap-3 cursor-pointer text-xs text-[#A3A3A3]">
								<input
									type="checkbox"
									v-model="confirmResetAnalytics"
									class="mt-0.5 rounded border-[#333333] text-[#FF6B00] focus:ring-[#FF6B00]"
								/>
								<span>
									{{ __('I understand that this action sets the displayed LMS analytics counters to zero without deleting any database records.') }}
								</span>
							</label>

							<button
								type="button"
								@click="executeResetAnalytics"
								:disabled="!confirmResetAnalytics || isExecutingReset"
								class="w-full py-3 px-4 rounded-xl bg-[#FF6B00] hover:bg-[#FF8C00] disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-sm shadow-md transition-all flex items-center justify-center gap-2"
							>
								<span v-if="isExecutingReset" class="animate-spin lucide-loader size-4" />
								<span v-else class="lucide-rotate-ccw size-4" />
								<span>{{ __('Confirm & Reset Analytics to 0') }}</span>
							</button>
						</div>
					</div>

					<!-- Option B: Delete Demo Data -->
					<div v-if="activeResetTab === 'demo'" class="space-y-4">
						<div class="p-4 rounded-xl border border-[#EF4444]/40 bg-[#EF4444]/10 space-y-2">
							<h4 class="text-sm font-bold text-red-300 flex items-center gap-2">
								<span class="lucide-alert-triangle size-4 text-[#EF4444]" />
								<span>{{ __('Destructive Administrative Action') }}</span>
							</h4>
							<p class="text-xs text-[#A3A3A3]">
								{{ __('Review and delete explicitly selected demo/test users and their associated records. Real student accounts and Administrator are strictly protected from deletion.') }}
							</p>
						</div>

						<!-- Demo Users List -->
						<div class="space-y-2">
							<div class="flex items-center justify-between text-xs">
								<span class="font-bold text-white">{{ __('Detected Test & Demo Accounts ({0})').format(demoUsersList.length) }}</span>
								<button
									v-if="demoUsersList.length"
									type="button"
									@click="toggleSelectAllDemo"
									class="text-[#FF6B00] hover:underline font-semibold"
								>
									{{ selectedDemoUsers.length === demoUsersList.length ? __('Deselect All') : __('Select All') }}
								</button>
							</div>

							<div
								v-if="isLoadingDemoUsers"
								class="py-8 text-center text-xs text-[#A3A3A3] flex items-center justify-center gap-2"
							>
								<LoadingIndicator class="size-4 text-[#FF6B00]" />
								<span>{{ __('Scanning for demo users...') }}</span>
							</div>

							<div
								v-else-if="demoUsersList.length"
								class="max-h-48 overflow-y-auto border border-[#333333] rounded-xl divide-y divide-[#333333] bg-[#111111]"
							>
								<label
									v-for="u in demoUsersList"
									:key="u.name"
									class="flex items-center justify-between p-3 hover:bg-[#1C1C1C] cursor-pointer transition-colors text-xs"
								>
									<div class="flex items-center gap-3">
										<input
											type="checkbox"
											:value="u.name"
											v-model="selectedDemoUsers"
											class="rounded border-[#333333] text-[#EF4444] focus:ring-[#EF4444]"
										/>
										<div>
											<div class="font-bold text-white">{{ u.full_name || u.name }}</div>
											<div class="text-[#A3A3A3] text-[11px]">{{ u.email }}</div>
										</div>
									</div>
									<div class="text-right text-[11px] text-[#A3A3A3]">
										<span>{{ u.enrollments_count }} {{ __('enrollments') }}</span>
									</div>
								</label>
							</div>

							<div
								v-else
								class="p-6 text-center border border-dashed border-[#333333] rounded-xl text-xs text-[#A3A3A3]"
							>
								{{ __('No demo or test user accounts found. All registered users are production accounts.') }}
							</div>
						</div>

						<!-- Secondary confirmation -->
						<div v-if="selectedDemoUsers.length" class="space-y-3 pt-2">
							<div class="space-y-1">
								<label class="block text-xs font-bold text-white">
									{{ __('Type "DELETE DEMO DATA" to confirm permanent deletion:') }}
								</label>
								<input
									type="text"
									v-model="deleteConfirmText"
									placeholder="DELETE DEMO DATA"
									class="w-full bg-[#111111] border border-[#333333] rounded-lg px-3 py-2 text-xs text-white focus:border-[#EF4444] outline-none"
								/>
							</div>

							<button
								type="button"
								@click="executeDeleteDemoData"
								:disabled="deleteConfirmText !== 'DELETE DEMO DATA' || isExecutingReset"
								class="w-full py-3 px-4 rounded-xl bg-[#EF4444] hover:bg-[#DC2626] disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-sm shadow-md transition-all flex items-center justify-center gap-2"
							>
								<span v-if="isExecutingReset" class="animate-spin lucide-loader size-4" />
								<span v-else class="lucide-trash-2 size-4" />
								<span>{{ __('Permanently Delete {0} Selected Account(s)').format(selectedDemoUsers.length) }}</span>
							</button>
						</div>
					</div>
				</div>

				<!-- Modal Footer -->
				<div class="p-4 border-t border-[#333333] bg-[#111111] flex justify-end">
					<button
						type="button"
						@click="closeResetModal"
						class="px-4 py-2 rounded-lg bg-[#252525] hover:bg-[#333333] text-white text-xs font-semibold transition-colors"
					>
						{{ __('Close') }}
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import {
	call,
	createResource,
	LoadingIndicator,
	usePageMeta,
} from 'frappe-ui'
import { DonutChart, LineChart } from 'frappe-ui/charts'
import { computed, ref, onMounted } from 'vue'
import PageHeader from '@/components/Layouts/PageHeader.vue'
import ChartEmptyState from '@/components/ChartEmptyState.vue'
import { compactNumber } from '@/utils/numberCardFormat'
import { sessionStore } from '../stores/session'
import { usersStore } from '../stores/user'

const { brand } = sessionStore()
const { userResource } = usersStore()

const isSystemManager = computed(() => {
	const user = userResource.data
	return Boolean(user?.is_system_manager || user?.name === 'Administrator')
})

const breadcrumbs = computed(() => [
	{
		label: __('Statistics'),
		route: { name: 'Statistics' },
	},
])

const selectedDateRange = ref('all')
const isRefreshing = ref(false)

const chartDetails = createResource({
	url: 'lms.lms.api.get_chart_details',
	params: {
		date_range: selectedDateRange.value,
	},
	auto: true,
})

const signupsChart = createResource({
	url: 'lms.lms.utils.get_chart_data',
	params: {
		chart_name: 'New Signups',
	},
	auto: true,
})

const enrollmentChart = createResource({
	url: 'lms.lms.utils.get_chart_data',
	params: {
		chart_name: 'Course Enrollments',
	},
	auto: true,
})

const certification = createResource({
	url: 'lms.lms.utils.get_chart_data',
	params: {
		chart_name: 'Certification',
	},
	auto: true,
})

const courseCompletion = createResource({
	url: 'lms.lms.utils.get_course_completion_data',
	auto: true,
})

const hasPoints = (data) => Boolean(data?.some((point) => point.count > 0))

const hasCompletions = computed(() => {
	const completed = courseCompletion.data?.find((d) => d.label === 'Completed')
	return (completed?.value || 0) > 0
})

const onDateRangeChange = () => {
	chartDetails.params = { date_range: selectedDateRange.value }
	chartDetails.fetch()
}

const refreshStatistics = async () => {
	isRefreshing.value = true
	try {
		await Promise.all([
			chartDetails.fetch(),
			signupsChart.fetch(),
			enrollmentChart.fetch(),
			certification.fetch(),
			courseCompletion.fetch(),
		])
	} catch (e) {
		console.error(e)
	} finally {
		setTimeout(() => {
			isRefreshing.value = false
		}, 400)
	}
}

// ==========================================
// Reset Statistics Management Modal State
// ==========================================
const showResetModal = ref(false)
const activeResetTab = ref('analytics') // 'analytics' | 'demo'
const confirmResetAnalytics = ref(false)
const isExecutingReset = ref(false)
const modalMessage = ref(null)

const demoUsersList = ref([])
const selectedDemoUsers = ref([])
const isLoadingDemoUsers = ref(false)
const deleteConfirmText = ref('')

const openResetModal = async () => {
	showResetModal.value = true
	confirmResetAnalytics.value = false
	deleteConfirmText.value = ''
	modalMessage.value = null
	await loadDemoUsers()
}

const closeResetModal = () => {
	showResetModal.value = false
	modalMessage.value = null
	confirmResetAnalytics.value = false
	deleteConfirmText.value = ''
}

const loadDemoUsers = async () => {
	isLoadingDemoUsers.value = true
	try {
		const res = await call('lms.lms.api.get_demo_users')
		demoUsersList.value = res || []
		// Auto select users marked as suggested demo
		selectedDemoUsers.value = demoUsersList.value
			.filter((u) => u.is_suggested_demo)
			.map((u) => u.name)
	} catch (err) {
		console.error('Error loading demo users', err)
		demoUsersList.value = []
	} finally {
		isLoadingDemoUsers.value = false
	}
}

const toggleSelectAllDemo = () => {
	if (selectedDemoUsers.value.length === demoUsersList.value.length) {
		selectedDemoUsers.value = []
	} else {
		selectedDemoUsers.value = demoUsersList.value.map((u) => u.name)
	}
}

// Option A Execution: Reset Analytics
const executeResetAnalytics = async () => {
	if (!confirmResetAnalytics.value) return
	isExecutingReset.value = true
	modalMessage.value = null

	try {
		const res = await call('lms.lms.api.reset_lms_analytics', { action: 'reset' })
		modalMessage.value = {
			isError: false,
			text: res.message || __('Analytics reset successfully!'),
		}
		confirmResetAnalytics.value = false
		await refreshStatistics()
	} catch (err) {
		modalMessage.value = {
			isError: true,
			text: err.messages?.[0] || err.message || __('Failed to reset analytics.'),
		}
	} finally {
		isExecutingReset.value = false
	}
}

// Restore Full History
const restoreHistoricalAnalytics = async () => {
	if (!confirm(__('Are you sure you want to restore full historical LMS analytics?'))) return
	try {
		await call('lms.lms.api.reset_lms_analytics', { action: 'restore' })
		await refreshStatistics()
	} catch (err) {
		console.error(err)
	}
}

// Option B Execution: Delete Demo Data
const executeDeleteDemoData = async () => {
	if (deleteConfirmText.value !== 'DELETE DEMO DATA' || !selectedDemoUsers.value.length) return
	isExecutingReset.value = true
	modalMessage.value = null

	try {
		const res = await call('lms.lms.api.delete_demo_data', {
			users: selectedDemoUsers.value,
		})
		modalMessage.value = {
			isError: false,
			text: res.message || __('Selected demo users deleted successfully!'),
		}
		selectedDemoUsers.value = []
		deleteConfirmText.value = ''
		await loadDemoUsers()
		await refreshStatistics()
	} catch (err) {
		modalMessage.value = {
			isError: true,
			text: err.messages?.[0] || err.message || __('Failed to delete demo data.'),
		}
	} finally {
		isExecutingReset.value = false
	}
}

usePageMeta(() => ({
	title: __('Statistics'),
	icon: brand.favicon,
}))
</script>

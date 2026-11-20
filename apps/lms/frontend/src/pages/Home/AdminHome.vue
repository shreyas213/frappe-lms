<template>
	<div class="space-y-8 pb-12">
		<!-- Executive KPI Stats Bar -->
		<div v-if="adminMetrics.loading && !adminMetrics.data" class="flex items-center justify-center py-12 text-[#A3A3A3]">
			<LoadingIndicator class="size-6 text-[#FF6B00] mr-2" />
			<span class="text-sm">{{ __('Loading administrator metrics...') }}</span>
		</div>

		<div v-else-if="adminMetrics.data" class="space-y-6">
			<!-- Quick Actions Toolbar -->
			<div class="flex flex-wrap items-center justify-between gap-3 p-4 rounded-xl bg-[#1C1C1C] border border-[#333333] shadow-sm">
				<div class="flex items-center gap-2">
					<span class="size-2.5 rounded-full bg-[#22C55E] animate-pulse" />
					<span class="text-xs font-bold uppercase tracking-wider text-white">
						{{ __('Platform Overview & Management') }}
					</span>
				</div>

				<div class="flex items-center gap-2 flex-wrap">
					<Button
						variant="solid"
						:route="{ name: 'NewCourse' }"
						@click="setFormSource('admin_home')"
					>
						<template #prefix>
							<span class="lucide-plus size-4" />
						</template>
						{{ __('New Course') }}
					</Button>

					<Button
						variant="subtle"
						:route="{ name: 'BatchForm', params: { batchName: 'new' } }"
					>
						<template #prefix>
							<span class="lucide-users size-4" />
						</template>
						{{ __('New Batch') }}
					</Button>

					<Button
						variant="subtle"
						:route="{ name: 'JobForm', params: { jobName: 'new' } }"
					>
						<template #prefix>
							<span class="lucide-briefcase size-4" />
						</template>
						{{ __('Post Job') }}
					</Button>

					<Button
						variant="subtle"
						:route="{ name: 'CertifiedParticipants' }"
					>
						<template #prefix>
							<span class="lucide-award size-4" />
						</template>
						{{ __('Certificates') }}
					</Button>

					<Button
						variant="subtle"
						:route="{ name: 'Statistics' }"
					>
						<template #prefix>
							<span class="lucide-trending-up size-4" />
						</template>
						{{ __('Analytics') }}
					</Button>
				</div>
			</div>

			<!-- KPI Cards Grid (Real-time MariaDB values) -->
			<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
				<!-- KPI 1: Students -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF6B00]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Students') }}</span>
						<div class="p-2 rounded-lg bg-[#FF6B00]/15 text-[#FF6B00]">
							<span class="lucide-users size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ adminMetrics.data.total_students }}
					</div>
					<div class="text-xs text-[#22C55E] mt-1 flex items-center gap-1">
						<span class="size-1.5 rounded-full bg-[#22C55E]" />
						<span>{{ adminMetrics.data.active_students }} {{ __('active in 30d') }}</span>
					</div>
				</div>

				<!-- KPI 2: Courses (Published vs Draft) -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF6B00]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Courses') }}</span>
						<div class="p-2 rounded-lg bg-[#FF8C00]/15 text-[#FF8C00]">
							<span class="lucide-book-open size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ adminMetrics.data.total_courses }}
					</div>
					<div class="text-xs text-[#A3A3A3] mt-1 flex items-center gap-2">
						<span class="text-[#22C55E] font-medium">{{ adminMetrics.data.published_courses }} {{ __('pub') }}</span>
						<span>•</span>
						<span class="text-amber-400 font-medium">{{ adminMetrics.data.draft_courses }} {{ __('draft') }}</span>
					</div>
				</div>

				<!-- KPI 3: Enrollments & Completion Rate -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF6B00]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Enrollments') }}</span>
						<div class="p-2 rounded-lg bg-[#22C55E]/15 text-[#22C55E]">
							<span class="lucide-user-check size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ adminMetrics.data.total_enrollments }}
					</div>
					<div class="text-xs text-[#A3A3A3] mt-1 flex items-center gap-1.5">
						<span>{{ __('Rate:') }}</span>
						<span class="font-bold text-[#FF6B00]">{{ adminMetrics.data.completion_rate }}%</span>
						<span>({{ adminMetrics.data.completed_enrollments }} {{ __('done') }})</span>
					</div>
				</div>

				<!-- KPI 4: Certificates Issued -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF6B00]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Certificates') }}</span>
						<div class="p-2 rounded-lg bg-[#FF6B00]/15 text-[#FF6B00]">
							<span class="lucide-award size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ adminMetrics.data.certificates_issued }}
					</div>
					<div class="text-xs text-[#A3A3A3] mt-1">
						{{ __('Issued credentials') }}
					</div>
				</div>

				<!-- KPI 5: Batches -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF6B00]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Batches') }}</span>
						<div class="p-2 rounded-lg bg-purple-500/15 text-purple-400">
							<span class="lucide-calendar-days size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ adminMetrics.data.total_batches }}
					</div>
					<div class="text-xs text-[#A3A3A3] mt-1">
						{{ __('Cohorts created') }}
					</div>
				</div>

				<!-- KPI 6: Active Jobs -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF6B00]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Jobs') }}</span>
						<div class="p-2 rounded-lg bg-blue-500/15 text-blue-400">
							<span class="lucide-briefcase size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ adminMetrics.data.active_jobs }}
					</div>
					<div class="text-xs text-[#A3A3A3] mt-1">
						{{ __('Active listings') }}
					</div>
				</div>

				<!-- KPI 7: Instructors -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF6B00]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Instructors') }}</span>
						<div class="p-2 rounded-lg bg-emerald-500/15 text-emerald-400">
							<span class="lucide-graduation-cap size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ adminMetrics.data.total_instructors }}
					</div>
					<div class="text-xs text-[#A3A3A3] mt-1">
						{{ __('Assigned faculty') }}
					</div>
				</div>

				<!-- KPI 8: Completion Progress Meter -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF6B00]/50 transition-colors flex flex-col justify-between">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-1">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Completion') }}</span>
						<span class="text-xs font-bold text-[#FF6B00]">{{ adminMetrics.data.completion_rate }}%</span>
					</div>
					<div class="w-full bg-[#111111] rounded-full h-2 overflow-hidden border border-[#333333] my-1">
						<div
							class="bg-[#FF6B00] h-2 rounded-full transition-all duration-500"
							:style="{ width: `${Math.min(adminMetrics.data.completion_rate, 100)}%` }"
						/>
					</div>
					<div class="text-[11px] text-[#A3A3A3]">
						{{ __('Overall syllabus completion') }}
					</div>
				</div>
			</div>

			<!-- Recent Activity Feed (Recent Enrollments & Recent Certificates) -->
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
				<!-- Recent Enrollments -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-5 shadow-sm space-y-3">
					<div class="flex items-center justify-between border-b border-[#333333] pb-2.5">
						<h3 class="font-bold text-white text-sm flex items-center gap-2">
							<span class="lucide-user-plus size-4 text-[#FF6B00]" />
							<span>{{ __('Recent Student Enrollments') }}</span>
						</h3>
					</div>

					<div v-if="adminMetrics.data.recent_enrollments?.length" class="divide-y divide-[#333333]">
						<div
							v-for="e in adminMetrics.data.recent_enrollments"
							:key="e.name"
							class="py-2.5 first:pt-0 last:pb-0 flex items-center justify-between gap-3 text-xs"
						>
							<div class="min-w-0 space-y-0.5">
								<div class="font-semibold text-white truncate">
									{{ e.student_name }}
								</div>
								<div class="text-[#A3A3A3] truncate">
									{{ e.course_title }}
								</div>
							</div>

							<div class="text-right shrink-0">
								<span class="font-bold text-[#FF8C00]">{{ e.progress }}%</span>
								<div class="text-[10px] text-[#777777]">{{ formatDate(e.enrolled_on) }}</div>
							</div>
						</div>
					</div>
					<div v-else class="text-xs text-[#A3A3A3] py-4 text-center">
						{{ __('No recent enrollments found.') }}
					</div>
				</div>

				<!-- Recent Certificates Issued -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-5 shadow-sm space-y-3">
					<div class="flex items-center justify-between border-b border-[#333333] pb-2.5">
						<h3 class="font-bold text-white text-sm flex items-center gap-2">
							<span class="lucide-award size-4 text-[#FF8C00]" />
							<span>{{ __('Recent Certificates Issued') }}</span>
						</h3>
						<router-link
							:to="{ name: 'CertifiedParticipants' }"
							class="text-xs text-[#FF6B00] hover:text-[#FF8C00] font-semibold flex items-center gap-1"
						>
							<span>{{ __('View all') }}</span>
							<span class="lucide-arrow-right size-3" />
						</router-link>
					</div>

					<div v-if="adminMetrics.data.recent_certificates?.length" class="divide-y divide-[#333333]">
						<div
							v-for="c in adminMetrics.data.recent_certificates"
							:key="c.name"
							class="py-2.5 first:pt-0 last:pb-0 flex items-center justify-between gap-3 text-xs"
						>
							<div class="min-w-0 space-y-0.5">
								<div class="font-semibold text-white truncate">
									{{ c.member_name }}
								</div>
								<div class="text-[#A3A3A3] truncate">
									{{ c.course_title }}
								</div>
							</div>

							<div class="text-right shrink-0">
								<a
									:href="`/certificate?certificate_id=${c.name}`"
									target="_blank"
									class="font-mono text-[#FF6B00] hover:underline"
								>
									{{ c.name }}
								</a>
								<div class="text-[10px] text-[#777777]">{{ formatDate(c.issue_date) }}</div>
							</div>
						</div>
					</div>
					<div v-else class="text-xs text-[#A3A3A3] py-4 text-center">
						{{ __('No certificates issued yet.') }}
					</div>
				</div>
			</div>
		</div>

		<!-- Upcoming Evaluations Section -->
		<div v-if="evals?.data?.length" class="space-y-3">
			<div class="text-base font-bold text-white">
				{{ __('Upcoming Evaluations') }}
			</div>
			<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
				<component
					:is="user.data?.username ? 'router-link' : 'div'"
					v-for="evaluation in evals?.data"
					:key="evaluation.name"
					:to="profileRoute(user.data?.username, 'ProfileEvaluationSchedule')"
					class="border border-[#333333] bg-[#1C1C1C] rounded-xl p-4 flex flex-col justify-between"
				>
					<div class="text-white font-bold text-sm mb-3">
						{{ evaluation.course_title }}
					</div>
					<div class="text-[#A3A3A3] text-xs space-y-2">
						<div class="flex items-center gap-2">
							<span class="lucide-calendar size-3.5" />
							<span>{{ dayjs(evaluation.date).format('DD MMMM YYYY') }}</span>
						</div>
						<div class="flex items-center gap-2">
							<span class="lucide-clock size-3.5" />
							<span>{{ formatTime(evaluation.start_time) }}</span>
						</div>
						<div class="flex items-center gap-2">
							<span class="lucide-graduation-cap size-3.5" />
							<span>{{ evaluation.member_name }}</span>
						</div>
					</div>
				</component>
			</div>
		</div>

		<!-- Upcoming Live Classes Section -->
		<div v-if="liveClasses?.data?.length" class="space-y-3">
			<div class="text-base font-bold text-white">
				{{ __('Upcoming Live Classes') }}
			</div>
			<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
				<div
					v-for="cls in liveClasses?.data"
					:key="cls.name"
					class="border border-[#333333] bg-[#1C1C1C] rounded-xl p-4 space-y-3"
				>
					<div class="text-white font-bold text-sm">
						{{ cls.title }}
					</div>
					<div class="text-[#A3A3A3] text-xs line-clamp-2">
						{{ cls.description }}
					</div>
					<LiveClassCard
						:cls="cls"
						class="space-y-3"
						ended-class="text-ink-amber-5"
					/>
				</div>
			</div>
		</div>

		<!-- Courses Created Section -->
		<div v-if="createdCourses.data?.length" class="space-y-4">
			<div class="flex items-center justify-between border-b border-[#333333] pb-2">
				<span class="text-base font-bold text-white">
					{{ __('Courses Created') }} ({{ createdCourses.data.length }})
				</span>
				<router-link :to="{ name: 'Courses' }">
					<span class="flex items-center gap-1 text-[#FF6B00] hover:text-[#FF8C00] text-xs font-semibold">
						<span>{{ __('See all') }}</span>
						<span class="lucide-arrow-right size-3" />
					</span>
				</router-link>
			</div>
			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
				<router-link
					v-for="course in createdCourses.data"
					:key="course.name"
					:to="{ name: 'CourseDetail', params: { courseName: course.name } }"
				>
					<CourseCard :course="course" />
				</router-link>
			</div>
		</div>

		<!-- Batches Created Section -->
		<div v-if="createdBatches.data?.length" class="space-y-4">
			<div class="flex items-center justify-between border-b border-[#333333] pb-2">
				<span class="text-base font-bold text-white">
					{{ __('Batches') }} ({{ createdBatches.data.length }})
				</span>
				<router-link :to="{ name: 'Batches' }">
					<span class="flex items-center gap-1 text-[#FF6B00] hover:text-[#FF8C00] text-xs font-semibold">
						<span>{{ __('See all') }}</span>
						<span class="lucide-arrow-right size-3" />
					</span>
				</router-link>
			</div>
			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
				<router-link
					v-for="batch in createdBatches.data"
					:key="batch.name"
					:to="{ name: 'BatchDetail', params: { batchName: batch.name } }"
				>
					<BatchCard :batch="batch" />
				</router-link>
			</div>
		</div>

		<!-- Empty state fallback if neither courses nor batches exist -->
		<div
			v-if="!createdCourses.data?.length && !createdBatches.data?.length"
			class="flex flex-col items-center justify-center py-16 text-center space-y-3"
		>
			<span class="lucide-graduation-cap size-10 text-[#FF6B00]" />
			<div class="text-base font-bold text-white">
				{{ __('No courses created yet') }}
			</div>
			<div class="text-xs text-[#A3A3A3] max-w-sm">
				{{ __('Create your first course to begin managing curriculum, uploading lessons, and enrolling students.') }}
			</div>
			<Button
				:route="{ name: 'NewCourse' }"
				variant="solid"
				@click="setFormSource('admin_home')"
			>
				<template #prefix>
					<span class="lucide-plus size-4" />
				</template>
				{{ __('New Course') }}
			</Button>
		</div>
	</div>
</template>

<script setup>
import { Button, createResource, LoadingIndicator } from 'frappe-ui'
import { inject, onMounted } from 'vue'
import { formatTime } from '@/utils'
import { formatTimezone } from '@/utils/timezone'
import { profileRoute } from '@/utils/routes'
import CourseCard from '@/components/CourseCard.vue'
import { setFormSource } from '@/composables/formTracking'
import BatchCard from '@/pages/Batches/components/BatchCard.vue'
import LiveClassCard from '@/pages/Home/LiveClassCard.vue'

const user = inject('$user')
const dayjs = inject('$dayjs')

const props = defineProps({
	liveClasses: {
		type: Object,
		default: () => ({}),
	},
	evals: {
		type: Object,
		default: () => ({}),
	},
})

const adminMetrics = createResource({
	url: 'lms.lms.api.get_admin_dashboard_metrics',
	auto: true,
})

const createdCourses = createResource({
	url: 'lms.lms.api.get_created_courses',
	auto: true,
})

const createdBatches = createResource({
	url: 'lms.lms.api.get_created_batches',
	auto: true,
})

onMounted(() => {
	adminMetrics.reload()
	createdCourses.reload()
	createdBatches.reload()
})

const formatDate = (dateStr) => {
	if (!dateStr) return ''
	try {
		return dayjs(dateStr).format('DD MMM YYYY')
	} catch (e) {
		return dateStr
	}
}
</script>

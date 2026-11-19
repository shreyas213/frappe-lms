<template>
	<div class="space-y-8 mt-6 mb-12">
		<!-- Account Details Card (for student/user) -->
		<div
			v-if="profile.data"
			class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-5 shadow-sm"
		>
			<h2 class="text-base font-bold text-white mb-4 flex items-center gap-2">
				<span class="lucide-user size-4 text-[#FF6B00]" />
				<span>{{ __('Account Details') }}</span>
			</h2>

			<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
				<div class="space-y-1">
					<div class="text-xs text-[#A3A3A3]">{{ __('Full Name') }}</div>
					<div class="font-semibold text-white">{{ profile.data.full_name || '-' }}</div>
				</div>

				<div class="space-y-1">
					<div class="text-xs text-[#A3A3A3]">{{ __('Email Address') }}</div>
					<div class="font-semibold text-white truncate">
						{{ profile.data.name || user.data?.email || '-' }}
					</div>
				</div>

				<div class="space-y-1">
					<div class="text-xs text-[#A3A3A3]">{{ __('Username') }}</div>
					<div class="font-semibold text-white">@{{ profile.data.username || '-' }}</div>
				</div>

				<div class="space-y-1">
					<div class="text-xs text-[#A3A3A3]">{{ __('Member Since') }}</div>
					<div class="font-semibold text-white">
						{{ profile.data.creation ? dayjs(profile.data.creation).format('MMMM YYYY') : '-' }}
					</div>
				</div>
			</div>
		</div>

		<!-- Learning Progress & Courses (for logged in student viewing their own profile) -->
		<div
			v-if="isSessionUser && studentDashboard.data"
			class="space-y-6"
		>
			<!-- Learning Stats Summary -->
			<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-5 shadow-sm space-y-4">
				<h2 class="text-base font-bold text-white flex items-center gap-2">
					<span class="lucide-graduation-cap size-4 text-[#FF6B00]" />
					<span>{{ __('Learning Progress & Performance') }}</span>
				</h2>

				<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
					<div class="p-3 rounded-lg bg-[#111111] border border-[#333333] text-center">
						<div class="text-2xl font-bold text-white">
							{{ studentStats.total_enrolled }}
						</div>
						<div class="text-xs text-[#A3A3A3] mt-1">{{ __('Enrolled Courses') }}</div>
					</div>

					<div class="p-3 rounded-lg bg-[#FF8C00]/15 border border-[#FF8C00]/30 text-center">
						<div class="text-2xl font-bold text-[#FF8C00]">
							{{ studentStats.in_progress }}
						</div>
						<div class="text-xs text-[#A3A3A3] mt-1">{{ __('In Progress') }}</div>
					</div>

					<div class="p-3 rounded-lg bg-[#22C55E]/15 border border-[#22C55E]/30 text-center">
						<div class="text-2xl font-bold text-[#22C55E]">
							{{ studentStats.completed }}
						</div>
						<div class="text-xs text-[#A3A3A3] mt-1">{{ __('Completed') }}</div>
					</div>

					<div class="p-3 rounded-lg bg-[#FF6B00]/15 border border-[#FF6B00]/30 text-center">
						<div class="text-2xl font-bold text-[#FF6B00]">
							{{ studentStats.certificates_count }}
						</div>
						<div class="text-xs text-[#A3A3A3] mt-1">{{ __('Certificates Earned') }}</div>
					</div>
				</div>
			</div>

			<!-- Enrolled Courses List -->
			<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-5 shadow-sm space-y-4">
				<div class="flex items-center justify-between">
					<h2 class="text-base font-bold text-white flex items-center gap-2">
						<span class="lucide-book-open size-4 text-[#FF6B00]" />
						<span>{{ __('Enrolled Courses') }} ({{ enrolledCourses.length }})</span>
					</h2>
					<router-link
						:to="{ name: 'Courses' }"
						class="text-xs text-[#FF6B00] hover:text-[#FF8C00] font-semibold flex items-center gap-1"
					>
						<span>{{ __('Browse More') }}</span>
						<span class="lucide-arrow-right size-3" />
					</router-link>
				</div>

				<div v-if="enrolledCourses.length" class="divide-y divide-[#333333]">
					<div
						v-for="course in enrolledCourses"
						:key="course.name"
						class="py-4 first:pt-0 last:pb-0 flex flex-col md:flex-row md:items-center justify-between gap-4"
					>
						<div class="space-y-1.5 flex-1 min-w-0">
							<div class="flex items-center gap-2">
								<router-link
									:to="{ name: 'CourseDetail', params: { courseName: course.name } }"
									class="font-bold text-white hover:text-[#FF6B00] transition-colors truncate"
								>
									{{ course.title }}
								</router-link>
								<span
									v-if="course.is_completed"
									class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-[#22C55E]/20 text-[#22C55E] border border-[#22C55E]/30"
								>
									<span class="lucide-check size-3" />
									{{ __('Completed') }}
								</span>
							</div>

							<div class="text-xs text-[#A3A3A3] flex items-center gap-3">
								<span>{{ course.completed_lessons }} / {{ course.total_lessons }} {{ __('lessons') }}</span>
								<span>•</span>
								<span class="font-semibold text-[#FF6B00]">{{ course.progress }}%</span>
							</div>

							<!-- Course Progress Bar -->
							<div class="w-full max-w-sm bg-[#111111] rounded-full h-1.5 overflow-hidden border border-[#333333]">
								<div
									class="h-1.5 rounded-full transition-all duration-300"
									:class="course.is_completed ? 'bg-[#22C55E]' : 'bg-[#FF6B00]'"
									:style="{ width: `${Math.min(course.progress, 100)}%` }"
								/>
							</div>
						</div>

						<div class="flex items-center gap-2 shrink-0">
							<router-link
								:to="{
									name: 'Lesson',
									params: {
										courseName: course.name,
										chapterNumber: (course.current_lesson_index || '1-1').split('-')[0],
										lessonNumber: (course.current_lesson_index || '1-1').split('-')[1],
									},
								}"
								class="px-4 py-2 rounded-lg text-xs font-semibold bg-[#FF6B00] hover:bg-[#FF8C00] text-white transition-colors flex items-center gap-1.5 shadow"
							>
								<span class="lucide-play size-3 fill-white" />
								<span>{{ course.is_completed ? __('Review') : __('Continue') }}</span>
							</router-link>

							<router-link
								v-if="course.is_completed && course.enable_certification"
								:to="{ name: 'CourseCertification', params: { courseName: course.name } }"
								class="p-2 rounded-lg text-xs font-semibold text-[#FF8C00] bg-[#FF6B00]/15 hover:bg-[#FF6B00]/25 border border-[#FF6B00]/30 transition-colors"
								:title="__('View Certificate')"
							>
								<span class="lucide-award size-4" />
							</router-link>
						</div>
					</div>
				</div>

				<div v-else class="text-center py-6 text-xs text-[#A3A3A3]">
					<p>{{ __('No courses enrolled yet.') }}</p>
					<router-link
						:to="{ name: 'Courses' }"
						class="mt-2 inline-block font-semibold text-[#FF6B00] hover:underline"
					>
						{{ __('Explore available courses') }}
					</router-link>
				</div>
			</div>
		</div>

		<!-- About (Bio) Section -->
		<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-5 shadow-sm space-y-3">
			<h2 class="text-base font-bold text-white flex items-center gap-2">
				<span class="lucide-align-left size-4 text-[#FF6B00]" />
				<span>{{ __('About') }}</span>
			</h2>
			<div
				v-if="profile.data.bio"
				v-safe-html:bio="decodeEntities(profile.data.bio)"
				class="ProseMirror prose prose-invert prose-table:table-fixed prose-td:p-2 prose-th:p-2 prose-td:border prose-th:border prose-td:border-[#333333] prose-th:border-[#333333] prose-td:relative prose-th:relative prose-th:bg-[#111111] prose-sm max-w-none !whitespace-normal text-[#E5E5E5]"
			></div>
			<div v-else class="text-[#A3A3A3] text-sm italic">
				{{ __('No introduction written yet.') }}
			</div>
		</div>

		<!-- Achievements / Badges Section -->
		<div v-if="badges.data?.length" class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-5 shadow-sm space-y-4">
			<h2 class="text-base font-bold text-white flex items-center gap-2">
				<span class="lucide-medal size-4 text-[#FF8C00]" />
				<span>{{ __('Achievements') }}</span>
			</h2>
			<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
				<div v-for="badge in badges.data" :key="badge.badge">
					<HoverCard :leave-delay="10">
						<template #trigger>
							<div class="relative flex flex-col items-center p-3 rounded-lg border border-[#333333] bg-[#111111] hover:border-[#FF6B00]/50 transition-colors">
								<img
									:src="safeUrl(badge.badge_image)"
									:alt="badge.badge"
									class="h-[70px] object-contain"
								/>
								<div class="text-xs font-semibold text-white mt-2 text-center line-clamp-1">
									{{ badge.badge }}
								</div>
								<div
									v-if="badge.count > 1"
									class="flex items-end bg-[#FF6B00]/20 text-[#FF8C00] p-1 text-[10px] font-bold rounded-full absolute end-1 bottom-1 border border-[#FF6B00]/30"
								>
									<span>x{{ badge.count }}</span>
								</div>
							</div>
						</template>
						<template #default>
							<div class="w-[250px] text-base p-4 space-y-2">
								<div class="font-bold text-sm">{{ badge.badge }}</div>
								<div class="text-xs text-ink-gray-6">{{ badge.badge_description }}</div>
								<div class="text-[11px] text-ink-gray-5">
									{{ __('Issued on:') }} {{ dayjs(badge.issued_on).format('DD MMM YYYY') }}
								</div>
							</div>
						</template>
					</HoverCard>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed, inject } from 'vue'
import { createResource, HoverCard } from 'frappe-ui'
import { decodeEntities } from '@/utils'
import { safeUrl } from '@/utils/safeUrl'

const dayjs = inject('$dayjs')
const user = inject('$user')

const props = defineProps({
	profile: {
		type: Object,
		required: true,
	},
})

const isSessionUser = computed(() => {
	return Boolean(user.data?.username && user.data.username === props.profile.data?.username)
})

const studentDashboard = createResource({
	url: 'lms.lms.api.get_student_dashboard_data',
	auto: true,
})

const studentStats = computed(() => studentDashboard.data?.stats || {
	total_enrolled: 0,
	in_progress: 0,
	completed: 0,
	certificates_count: 0,
	overall_progress: 0,
})

const enrolledCourses = computed(() => studentDashboard.data?.enrolled_courses || [])

const badges = createResource({
	url: 'lms.lms.api.get_badges',
	params: {
		member: props.profile.data.username,
	},
	auto: true,
	transform(data) {
		let finalBadges = []
		let groupedBadges = Object.groupBy(data, ({ badge }) => badge)
		for (let badge in groupedBadges) {
			let badgeData = groupedBadges[badge][0]
			badgeData.count = groupedBadges[badge].length
			finalBadges.push(badgeData)
		}
		return finalBadges
	},
})
</script>
<template>
	<div class="space-y-8 pb-12">
		<!-- Loading state -->
		<div
			v-if="dashboard.loading && !dashboard.data"
			class="flex flex-col items-center justify-center py-20 text-ink-gray-5"
		>
			<LoadingIndicator class="size-8 mb-3" />
			<p class="text-sm">{{ __('Loading your learning space...') }}</p>
		</div>

		<div v-else-if="dashboard.data" class="space-y-8">
			<!-- Hero / Welcome Banner -->
			<div
				class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#1C1C1C] via-[#231812] to-[#1C1C1C] border border-[#FF6B00]/30 p-6 md:p-8 text-white shadow-xl"
			>
				<div class="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
					<div class="space-y-2 max-w-2xl">
						<div class="inline-flex items-center gap-2 rounded-full bg-[#FF6B00]/20 border border-[#FF6B00]/40 px-3 py-1 text-xs font-semibold text-[#FF8C00] backdrop-blur-sm">
							<span>🔥</span>
							<span>{{ stats.streak || 0 }} {{ __('Day Learning Streak') }}</span>
						</div>
						<h1 class="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
							{{ __('Welcome back') }}, {{ studentInfo.full_name || user?.data?.full_name || __('Student') }}!
						</h1>
						<p class="text-[#A3A3A3] text-sm md:text-base leading-relaxed">
							{{
								stats.in_progress > 0
									? __('You have {0} courses in progress. Keep up the great momentum and achieve your goals!').format(stats.in_progress)
									: stats.total_enrolled > 0
									? __('All caught up! Revisit your completed courses or explore new learning paths.')
									: __('Start your learning journey today by exploring our wide range of expert-curated courses.')
							}}
						</p>
					</div>

					<!-- Quick student badge / Action -->
					<div class="flex flex-col bg-[#111111]/80 backdrop-blur-md rounded-xl p-3 border border-[#333333] min-w-[200px]">
						<div class="flex items-center gap-3">
							<UserAvatar
								:user="studentInfo"
								class="size-11 ring-2 ring-[#FF6B00]/50 rounded-full"
							/>
							<div class="text-left text-xs min-w-0">
								<div class="font-bold text-white text-sm truncate max-w-[130px]">
									{{ studentInfo.full_name }}
								</div>
								<div class="text-[#A3A3A3] truncate max-w-[130px]">
									{{ studentInfo.email }}
								</div>
								<router-link
									:to="{ name: 'Profile', params: { username: studentInfo.username || user?.data?.username } }"
									class="inline-flex items-center gap-1 text-[#FF6B00] hover:text-[#FF8C00] mt-0.5 font-semibold"
								>
									<span>{{ __('My Profile') }}</span>
									<span class="lucide-arrow-right size-3" />
								</router-link>
							</div>
						</div>
						<!-- Profile Completion Meter -->
						<div class="mt-2.5 pt-2 border-t border-[#333333]">
							<div class="flex items-center justify-between text-[11px] text-[#A3A3A3] mb-1">
								<span>{{ __('Profile Completion') }}</span>
								<span class="font-bold text-[#FF8C00]">{{ stats.profile_completion || 70 }}%</span>
							</div>
							<div class="w-full bg-[#222222] rounded-full h-1.5 overflow-hidden">
								<div class="bg-[#FF6B00] h-1.5 rounded-full transition-all duration-500" :style="{ width: `${stats.profile_completion || 70}%` }"></div>
							</div>
						</div>
					</div>
				</div>

				<!-- Subtle background decorative shapes -->
				<div class="absolute -right-12 -bottom-12 w-64 h-64 rounded-full bg-[#FF6B00]/5 blur-2xl pointer-events-none" />
				<div class="absolute right-1/3 -top-12 w-48 h-48 rounded-full bg-[#FF8C00]/5 blur-xl pointer-events-none" />
			</div>

			<!-- Dashboard KPI Stats Grid -->
			<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
				<!-- Stat 1: Total Enrolled -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF6B00]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Enrolled') }}</span>
						<div class="p-2 rounded-lg bg-[#FF6B00]/15 text-[#FF6B00]">
							<span class="lucide-book-open size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ stats.total_enrolled }}
					</div>
					<div class="text-xs text-[#A3A3A3] mt-1">
						{{ stats.total_enrolled === 1 ? __('Course total') : __('Courses total') }}
					</div>
				</div>

				<!-- Stat 2: In Progress -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF6B00]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('In Progress') }}</span>
						<div class="p-2 rounded-lg bg-[#FF8C00]/15 text-[#FF8C00]">
							<span class="lucide-hourglass size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ stats.in_progress }}
					</div>
					<div class="text-xs text-[#A3A3A3] mt-1">
						{{ __('Active learning') }}
					</div>
				</div>

				<!-- Stat 3: Completed Courses -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#22C55E]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Completed') }}</span>
						<div class="p-2 rounded-lg bg-[#22C55E]/15 text-[#22C55E]">
							<span class="lucide-check-circle size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ stats.completed }}
					</div>
					<div class="text-xs text-[#A3A3A3] mt-1">
						{{ __('Courses finished') }}
					</div>
				</div>

				<!-- Stat 4: Learning Hours -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF6B00]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Hours') }}</span>
						<div class="p-2 rounded-lg bg-[#FF6B00]/15 text-[#FF6B00]">
							<span class="lucide-clock size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ stats.learning_hours || 0 }} <span class="text-xs text-[#A3A3A3] font-normal">hrs</span>
					</div>
					<div class="text-xs text-[#A3A3A3] mt-1">
						{{ __('Learning time') }}
					</div>
				</div>

				<!-- Stat 5: Overall Progress -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF6B00]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Overall') }}</span>
						<div class="p-2 rounded-lg bg-[#FF6B00]/15 text-[#FF6B00]">
							<span class="lucide-trending-up size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ stats.overall_progress }}%
					</div>
					<div class="w-full bg-[#111111] rounded-full h-1.5 mt-2 overflow-hidden border border-[#333333]">
						<div
							class="bg-[#FF6B00] h-1.5 rounded-full transition-all duration-500"
							:style="{ width: `${Math.min(stats.overall_progress, 100)}%` }"
						/>
					</div>
				</div>

				<!-- Stat 6: Certificates -->
				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm hover:border-[#FF6B00]/50 transition-colors">
					<div class="flex items-center justify-between text-[#A3A3A3] mb-2">
						<span class="text-xs font-medium uppercase tracking-wider">{{ __('Certificates') }}</span>
						<div class="p-2 rounded-lg bg-[#FF8C00]/15 text-[#FF8C00]">
							<span class="lucide-award size-4" />
						</div>
					</div>
					<div class="text-2xl font-bold text-white">
						{{ stats.certificates_count }}
					</div>
					<div class="text-xs text-[#A3A3A3] mt-1">
						{{ __('Credentials earned') }}
					</div>
				</div>
			</div>

			<!-- Continue Learning Section -->
			<div v-if="continueCourse" class="space-y-3">
				<div class="flex items-center justify-between">
					<h2 class="text-lg font-bold text-white flex items-center gap-2">
						<span class="lucide-play-circle size-5 text-[#FF6B00]" />
						<span>{{ __('Continue Learning') }}</span>
					</h2>
					<router-link
						:to="{ name: 'CourseDetail', params: { courseName: continueCourse.name } }"
						class="text-xs text-[#FF6B00] hover:text-[#FF8C00] font-semibold flex items-center gap-1"
					>
						<span>{{ __('Course Outline') }}</span>
						<span class="lucide-arrow-right size-3" />
					</router-link>
				</div>

				<div class="rounded-2xl border border-[#333333] bg-[#1C1C1C] p-5 md:p-6 shadow-md hover:border-[#FF6B00]/40 transition-colors">
					<div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
						<div class="flex items-start gap-4">
							<div
								class="size-20 md:size-24 rounded-xl bg-cover bg-center shrink-0 border border-[#333333] shadow-inner overflow-hidden"
								:style="continueCourse.image ? { backgroundImage: `url('${encodeURI(continueCourse.image)}')` } : { background: 'linear-gradient(135deg, #FF6B00 0%, #FF8C00 100%)' }"
							>
								<div v-if="!continueCourse.image" class="w-full h-full flex items-center justify-center text-white font-bold text-xl">
									{{ continueCourse.title?.charAt(0) || 'C' }}
								</div>
							</div>

							<div class="space-y-1.5">
								<div class="flex items-center gap-2 flex-wrap">
									<span v-if="continueCourse.category" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-[#FF6B00]/20 text-[#FF8C00] border border-[#FF6B00]/30">
										{{ continueCourse.category }}
									</span>
									<span class="text-xs text-[#A3A3A3]">
										{{ continueCourse.completed_lessons }} / {{ continueCourse.total_lessons }} {{ __('lessons completed') }}
									</span>
								</div>

								<h3 class="text-lg md:text-xl font-bold text-white">
									{{ continueCourse.title }}
								</h3>

								<div class="flex items-center gap-2 text-sm text-[#A3A3A3]">
									<span class="font-medium text-[#FF6B00]">{{ __('Current:') }}</span>
									<span class="font-semibold text-white truncate max-w-xs md:max-w-md">
										{{ continueCourse.current_lesson_title || __('Next Lesson') }}
									</span>
								</div>

								<!-- Progress Bar -->
								<div class="w-full max-w-md pt-1">
									<div class="flex items-center justify-between text-xs text-[#A3A3A3] mb-1">
										<span>{{ __('Course progress') }}</span>
										<span class="font-bold text-[#FF6B00]">{{ continueCourse.progress }}%</span>
									</div>
									<div class="w-full bg-[#111111] rounded-full h-2 overflow-hidden border border-[#333333]">
										<div
											class="bg-[#FF6B00] h-2 rounded-full transition-all duration-300"
											:style="{ width: `${Math.min(continueCourse.progress, 100)}%` }"
										/>
									</div>
								</div>
							</div>
						</div>

						<div class="flex items-center gap-3 w-full md:w-auto shrink-0 justify-end">
							<router-link
								:to="{
									name: 'Lesson',
									params: {
										courseName: continueCourse.name,
										chapterNumber: (continueCourse.current_lesson_index || '1-1').split('-')[0],
										lessonNumber: (continueCourse.current_lesson_index || '1-1').split('-')[1],
									},
								}"
								class="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-[#FF6B00] hover:bg-[#FF8C00] text-white font-semibold text-sm shadow hover:shadow-lg hover:shadow-[#FF6B00]/20 transition-all w-full md:w-auto"
							>
								<span class="lucide-play size-4 fill-white" />
								<span>{{ __('Resume Lesson') }}</span>
							</router-link>
						</div>
					</div>
				</div>
			</div>

			<!-- Enrolled Courses Section with Filter Tabs -->
			<div class="space-y-4">
				<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#333333] pb-3">
					<div>
						<h2 class="text-xl font-bold text-white">
							{{ __('My Enrolled Courses') }}
						</h2>
						<p class="text-xs text-[#A3A3A3]">
							{{ __('Track and continue your learning progress across all enrolled courses') }}
						</p>
					</div>

					<!-- Filter Pills -->
					<div class="flex items-center gap-2 bg-[#1C1C1C] border border-[#333333] p-1 rounded-lg text-xs font-medium self-start sm:self-auto">
						<button
							type="button"
							@click="courseFilter = 'all'"
							:class="courseFilter === 'all' ? 'bg-[#FF6B00] text-white shadow-sm' : 'text-[#A3A3A3] hover:text-white'"
							class="px-3 py-1.5 rounded-md transition-all font-semibold"
						>
							{{ __('All') }} ({{ stats.total_enrolled }})
						</button>
						<button
							type="button"
							@click="courseFilter = 'in_progress'"
							:class="courseFilter === 'in_progress' ? 'bg-[#FF6B00] text-white shadow-sm' : 'text-[#A3A3A3] hover:text-white'"
							class="px-3 py-1.5 rounded-md transition-all font-semibold"
						>
							{{ __('In Progress') }} ({{ stats.in_progress }})
						</button>
						<button
							type="button"
							@click="courseFilter = 'completed'"
							:class="courseFilter === 'completed' ? 'bg-[#FF6B00] text-white shadow-sm' : 'text-[#A3A3A3] hover:text-white'"
							class="px-3 py-1.5 rounded-md transition-all font-semibold"
						>
							{{ __('Completed') }} ({{ stats.completed }})
						</button>
					</div>
				</div>

				<!-- Course List Cards -->
				<div v-if="filteredCourses.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
					<div
						v-for="course in filteredCourses"
						:key="course.name"
						class="flex flex-col rounded-xl border border-[#333333] bg-[#1C1C1C] overflow-hidden shadow-sm hover:shadow-md hover:border-[#FF6B00]/50 transition-all"
					>
						<!-- Course Card Image -->
						<div
							class="h-40 bg-cover bg-center relative"
							:style="course.image ? { backgroundImage: `url('${encodeURI(course.image)}')` } : { background: 'linear-gradient(135deg, #1C1C1C 0%, #2A2A2A 100%)' }"
						>
							<div v-if="!course.image" class="w-full h-full flex items-center justify-center text-white font-bold text-xl px-4 text-center">
								{{ course.title }}
							</div>
							<div class="absolute top-3 left-3 flex gap-2">
								<span v-if="course.category" class="bg-black/75 backdrop-blur-md text-[#FF8C00] text-xs px-2.5 py-1 rounded-md font-semibold border border-[#333333]">
									{{ course.category }}
								</span>
							</div>
							<div class="absolute top-3 right-3">
								<span
									v-if="course.is_completed"
									class="inline-flex items-center gap-1 bg-[#22C55E] text-white text-xs px-2.5 py-1 rounded-md font-semibold shadow"
								>
									<span class="lucide-check size-3" />
									<span>{{ __('Completed') }}</span>
								</span>
								<span
									v-else
									class="bg-[#1C1C1C]/90 border border-[#333333] backdrop-blur-md text-[#FF6B00] text-xs px-2 py-1 rounded-md font-bold shadow"
								>
									{{ course.progress }}%
								</span>
							</div>
						</div>

						<!-- Course Card Content -->
						<div class="p-4 flex flex-col flex-1">
							<router-link
								:to="{ name: 'CourseDetail', params: { courseName: course.name } }"
								class="text-base font-bold text-white hover:text-[#FF6B00] transition-colors line-clamp-1 mb-1"
							>
								{{ course.title }}
							</router-link>

							<p class="text-xs text-[#A3A3A3] line-clamp-2 mb-4">
								{{ course.short_introduction || __('Master your skills with this comprehensive course.') }}
							</p>

							<!-- Progress Info -->
							<div class="mt-auto space-y-2">
								<div class="flex items-center justify-between text-xs text-[#A3A3A3]">
									<span>{{ course.completed_lessons }} / {{ course.total_lessons }} {{ __('Lessons') }}</span>
									<span class="font-semibold text-[#FF6B00]">{{ course.progress }}%</span>
								</div>

								<div class="w-full bg-[#111111] rounded-full h-1.5 overflow-hidden border border-[#333333]">
									<div
										class="h-1.5 rounded-full transition-all duration-300"
										:class="course.is_completed ? 'bg-[#22C55E]' : 'bg-[#FF6B00]'"
										:style="{ width: `${Math.min(course.progress, 100)}%` }"
									/>
								</div>

								<!-- Action Buttons -->
								<div class="pt-3 flex items-center gap-2">
									<router-link
										:to="{
											name: 'Lesson',
											params: {
												courseName: course.name,
												chapterNumber: (course.current_lesson_index || '1-1').split('-')[0],
												lessonNumber: (course.current_lesson_index || '1-1').split('-')[1],
											},
										}"
										class="flex-1 inline-flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-semibold text-white bg-[#FF6B00] hover:bg-[#FF8C00] transition-colors"
									>
										<span class="lucide-play size-3 fill-white" />
										<span>{{ course.is_completed ? __('Review Course') : __('Continue') }}</span>
									</router-link>

									<router-link
										v-if="course.is_completed && course.enable_certification"
										:to="{ name: 'CourseCertification', params: { courseName: course.name } }"
										class="inline-flex items-center justify-center p-2 rounded-lg text-xs font-semibold text-[#FF8C00] bg-[#FF6B00]/15 hover:bg-[#FF6B00]/25 border border-[#FF6B00]/30 transition-colors"
										:title="__('View Certificate')"
									>
										<span class="lucide-award size-4" />
									</router-link>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Empty State if no courses match filter -->
				<div
					v-else-if="enrolledCourses.length"
					class="p-8 text-center rounded-xl border border-dashed border-[#333333] bg-[#1C1C1C] text-[#A3A3A3]"
				>
					<p class="text-sm">{{ __('No courses match the selected filter.') }}</p>
					<button
						type="button"
						@click="courseFilter = 'all'"
						class="mt-2 text-xs font-semibold text-[#FF6B00] hover:underline"
					>
						{{ __('Show all courses') }}
					</button>
				</div>

				<!-- Empty State if not enrolled in any course -->
				<div
					v-else
					class="p-8 text-center rounded-2xl border-2 border-dashed border-[#333333] bg-[#1C1C1C] space-y-4"
				>
					<div class="size-16 rounded-full bg-[#FF6B00]/15 text-[#FF6B00] flex items-center justify-center mx-auto border border-[#FF6B00]/30">
						<span class="lucide-book-open size-8" />
					</div>
					<div class="space-y-1">
						<h3 class="text-lg font-bold text-white">
							{{ __('You are not enrolled in any courses yet') }}
						</h3>
						<p class="text-xs text-[#A3A3A3] max-w-md mx-auto">
							{{ __('Explore our catalog of top-rated courses taught by industry experts and start learning today.') }}
						</p>
					</div>
					<router-link
						:to="{ name: 'Courses' }"
						class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#FF6B00] hover:bg-[#FF8C00] text-white text-xs font-semibold shadow hover:shadow-md transition-all"
					>
						<span>{{ __('Browse Courses Catalog') }}</span>
						<span class="lucide-arrow-right size-3.5" />
					</router-link>
				</div>

				<!-- Available Top Courses Discovery for Students -->
				<div v-if="availableCourses.length" class="space-y-4 pt-4">
					<div class="flex items-center justify-between border-b border-[#333333] pb-2">
						<h3 class="text-lg font-bold text-white flex items-center gap-2">
							<span class="lucide-sparkles size-5 text-[#FF6B00]" />
							<span>{{ __('Discover Courses') }}</span>
						</h3>
						<router-link
							:to="{ name: 'Courses' }"
							class="text-xs text-[#FF6B00] hover:text-[#FF8C00] font-semibold flex items-center gap-1"
						>
							<span>{{ __('View all') }}</span>
							<span class="lucide-arrow-right size-3" />
						</router-link>
					</div>

					<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
						<div
							v-for="course in availableCourses"
							:key="course.name"
							class="rounded-xl border border-[#333333] bg-[#1C1C1C] overflow-hidden flex flex-col hover:border-[#FF6B00]/40 transition-colors"
						>
							<div
								class="h-32 bg-cover bg-center border-b border-[#333333] flex items-end p-3 relative"
								:style="course.image ? { backgroundImage: `url('${encodeURI(course.image)}')` } : { background: 'linear-gradient(135deg, #1C1C1C 0%, #2A2A2A 100%)' }"
							>
								<span v-if="course.category" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-[#FF6B00]/90 text-white backdrop-blur-sm shadow">
									{{ course.category }}
								</span>
							</div>

							<div class="p-4 flex flex-col flex-1">
								<router-link
									:to="{ name: 'CourseDetail', params: { courseName: course.name } }"
									class="text-base font-bold text-white hover:text-[#FF6B00] transition-colors line-clamp-1 mb-1"
								>
									{{ course.title }}
								</router-link>

								<p class="text-xs text-[#A3A3A3] line-clamp-2 mb-4">
									{{ course.short_introduction || __('Master your skills with this course.') }}
								</p>

								<div class="mt-auto pt-2 flex items-center justify-between border-t border-[#2A2A2A]">
									<div class="text-xs text-[#A3A3A3] truncate max-w-[140px]">
										{{ course.instructors?.[0]?.label || course.instructors?.[0]?.full_name || __('Frappe LMS') }}
									</div>
									<router-link
										:to="{ name: 'CourseDetail', params: { courseName: course.name } }"
										class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#FF6B00] hover:bg-[#FF8C00] text-white transition-colors"
									>
										{{ __('View Course') }}
									</router-link>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Two Column Layout: Recent Lessons & Earned Certificates -->
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
				<!-- Recent Lessons Completed -->
				<div class="space-y-3">
					<div class="flex items-center justify-between">
						<h2 class="text-lg font-bold text-white flex items-center gap-2">
							<span class="lucide-check-circle-2 size-5 text-[#22C55E]" />
							<span>{{ __('Recently Completed Lessons') }}</span>
						</h2>
					</div>

					<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm">
						<div v-if="recentLessons.length" class="divide-y divide-[#333333]">
							<div
								v-for="item in recentLessons"
								:key="item.lesson_name"
								class="py-3 first:pt-0 last:pb-0 flex items-center justify-between gap-3"
							>
								<div class="space-y-1 min-w-0">
									<div class="flex items-center gap-2">
										<span class="size-2 rounded-full bg-[#22C55E] shrink-0" />
										<span class="text-sm font-semibold text-white truncate">
											{{ item.lesson_title }}
										</span>
									</div>
									<div class="text-xs text-[#A3A3A3] flex items-center gap-2 pl-4">
										<span class="truncate max-w-[200px]">{{ item.course_title }}</span>
										<span>•</span>
										<span>{{ formatDate(item.completed_on) }}</span>
									</div>
								</div>

								<router-link
									:to="{
										name: 'Lesson',
										params: {
											courseName: item.course_name,
											chapterNumber: (item.lesson_index || '1-1').split('-')[0],
											lessonNumber: (item.lesson_index || '1-1').split('-')[1],
										},
									}"
									class="shrink-0 p-2 text-[#FF6B00] hover:bg-[#FF6B00]/10 rounded-lg transition-colors text-xs font-semibold inline-flex items-center gap-1"
								>
									<span>{{ __('Review') }}</span>
									<span class="lucide-arrow-right size-3" />
								</router-link>
							</div>
						</div>
						<div v-else class="text-center py-8 text-xs text-[#A3A3A3]">
							<span class="lucide-clock size-6 mx-auto mb-2 text-[#555555] block" />
							{{ __('No lessons completed yet. Start learning to track your activity!') }}
						</div>
					</div>
				</div>

				<!-- Earned Certificates -->
				<div class="space-y-3">
					<div class="flex items-center justify-between">
						<h2 class="text-lg font-bold text-white flex items-center gap-2">
							<span class="lucide-award size-5 text-[#FF8C00]" />
							<span>{{ __('Earned Certificates') }}</span>
						</h2>
						<router-link
							v-if="certificates.length"
							:to="{ name: 'ProfileCertificates', params: { username: studentInfo.username || user?.data?.username } }"
							class="text-xs text-[#FF6B00] hover:text-[#FF8C00] font-semibold flex items-center gap-1"
						>
							<span>{{ __('View all') }}</span>
							<span class="lucide-arrow-right size-3" />
						</router-link>
					</div>

					<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm">
						<div v-if="certificates.length" class="space-y-3">
							<div
								v-for="cert in certificates"
								:key="cert.name"
								class="p-3.5 rounded-lg border border-[#333333] bg-[#111111] flex items-center justify-between gap-3"
							>
								<div class="flex items-center gap-3 min-w-0">
									<div class="size-10 rounded-lg bg-[#FF6B00]/20 text-[#FF8C00] flex items-center justify-center shrink-0 border border-[#FF6B00]/30">
										<span class="lucide-graduation-cap size-5" />
									</div>
									<div class="min-w-0">
										<div class="text-sm font-bold text-white truncate">
											{{ cert.course_title || cert.batch_title || __('Course Certificate') }}
										</div>
										<div class="text-xs text-[#A3A3A3]">
											{{ __('Issued on:') }} {{ formatDate(cert.issue_date) }}
										</div>
									</div>
								</div>

								<div class="flex items-center gap-2 shrink-0">
									<a
										:href="cert.download_url"
										target="_blank"
										class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold bg-[#FF6B00] text-white hover:bg-[#FF8C00] shadow-sm transition-all"
										:title="__('Download PDF')"
									>
										<span class="lucide-download size-3.5" />
										<span>{{ __('PDF') }}</span>
									</a>
								</div>
							</div>
						</div>
						<div v-else class="text-center py-8 text-xs text-ink-gray-5">
							<span class="lucide-award size-6 mx-auto mb-2 text-ink-gray-4 block" />
							{{ __('Complete 100% of an eligible course to earn your verified certificate!') }}
						</div>
					</div>
				</div>
			</div>

			<!-- Upcoming Live Classes / Activities -->
			<div v-if="liveClasses.length" class="space-y-3">
				<h2 class="text-lg font-bold text-ink-gray-9 flex items-center gap-2">
					<span class="lucide-video size-5 text-rose-600" />
					<span>{{ __('Upcoming Live Classes') }}</span>
				</h2>

				<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
					<div
						v-for="cls in liveClasses"
						:key="cls.name"
						class="border rounded-xl bg-surface-white p-4 shadow-sm hover:border-outline-gray-3 transition-colors space-y-2"
					>
						<div class="font-bold text-ink-gray-9 leading-5">
							{{ cls.title }}
						</div>
						<div class="text-xs text-ink-gray-5 line-clamp-2">
							{{ cls.description }}
						</div>
						<LiveClassCard
							:cls="cls"
							class="pt-2"
						/>
					</div>
				</div>
			</div>

			<!-- Recommended Courses for You -->
			<div v-if="recommendedCourses.length" class="space-y-3">
				<div class="flex items-center justify-between">
					<h2 class="text-lg font-bold text-white flex items-center gap-2">
						<span class="lucide-sparkles size-5 text-[#FF6B00]" />
						<span>{{ __('Recommended For You') }}</span>
					</h2>
					<router-link
						:to="{ name: 'Courses' }"
						class="text-xs text-[#FF6B00] hover:text-[#FF8C00] font-semibold flex items-center gap-1"
					>
						<span>{{ __('Explore all') }}</span>
						<span class="lucide-arrow-right size-3" />
					</router-link>
				</div>

				<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
					<router-link
						v-for="c in recommendedCourses"
						:key="c.name"
						:to="{ name: 'CourseDetail', params: { courseName: c.name } }"
						class="rounded-xl border border-[#333333] bg-[#1C1C1C] hover:border-[#FF6B00]/50 p-4 transition-all flex flex-col justify-between group shadow-sm"
					>
						<div class="space-y-2.5">
							<div
								class="h-28 rounded-lg bg-cover bg-center border border-[#333333] overflow-hidden"
								:style="c.image ? { backgroundImage: `url('${encodeURI(c.image)}')` } : { background: 'linear-gradient(135deg, #262626 0%, #171717 100%)' }"
							>
								<div v-if="!c.image" class="w-full h-full flex items-center justify-center text-white/40 font-bold text-2xl">
									{{ c.title?.charAt(0) || 'C' }}
								</div>
							</div>
							<span v-if="c.category" class="inline-block px-2 py-0.5 rounded text-[11px] font-semibold bg-[#FF6B00]/15 text-[#FF8C00]">
								{{ c.category }}
							</span>
							<h4 class="font-bold text-white group-hover:text-[#FF6B00] transition-colors line-clamp-1 text-sm">
								{{ c.title }}
							</h4>
							<p class="text-xs text-[#A3A3A3] line-clamp-2">
								{{ c.short_introduction || __('Master new skills with this comprehensive course.') }}
							</p>
						</div>
						<div class="mt-4 pt-3 border-t border-[#333333] flex items-center justify-between text-xs">
							<span class="text-[#A3A3A3]">{{ c.paid_course ? `${c.currency || '$'}${c.course_price}` : __('Free') }}</span>
							<span class="text-[#FF6B00] font-semibold group-hover:translate-x-0.5 transition-transform inline-flex items-center gap-0.5">
								<span>{{ __('View Course') }}</span>
								<span class="lucide-chevron-right size-3" />
							</span>
						</div>
					</router-link>
				</div>
			</div>

			<!-- Recent Notifications Preview -->
			<div v-if="recentNotifications.length" class="space-y-3">
				<div class="flex items-center justify-between">
					<h2 class="text-lg font-bold text-white flex items-center gap-2">
						<span class="lucide-bell size-5 text-[#FF8C00]" />
						<span>{{ __('Recent Updates & Notifications') }}</span>
					</h2>
				</div>

				<div class="rounded-xl border border-[#333333] bg-[#1C1C1C] p-4 shadow-sm divide-y divide-[#333333]">
					<div
						v-for="notif in recentNotifications"
						:key="notif.name"
						class="py-2.5 first:pt-0 last:pb-0 flex items-center justify-between gap-3 text-xs"
					>
						<div class="flex items-center gap-2.5 min-w-0">
							<span
								class="size-2 rounded-full shrink-0"
								:class="notif.read ? 'bg-[#555555]' : 'bg-[#FF6B00]'"
							/>
							<span class="text-white truncate font-medium">
								{{ notif.subject }}
							</span>
						</div>
						<span class="text-[#A3A3A3] shrink-0">
							{{ formatDate(notif.creation) }}
						</span>
					</div>
				</div>
			</div>

			<!-- Evaluations Component -->
			<UpcomingEvaluations :forHome="true" />
		</div>
	</div>
</template>

<script setup>
import { computed, inject, onMounted, ref } from 'vue'
import { createResource, LoadingIndicator } from 'frappe-ui'
import UserAvatar from '@/components/UserAvatar.vue'
import LiveClassCard from '@/pages/Home/LiveClassCard.vue'
import UpcomingEvaluations from '@/components/UpcomingEvaluations.vue'

const user = inject('$user')
const dayjs = inject('$dayjs')

const props = defineProps({
	myLiveClasses: {
		type: Object,
		default: () => ({}),
	},
})

const courseFilter = ref('all')

const dashboard = createResource({
	url: 'lms.lms.api.get_student_dashboard_data',
	auto: true,
})

onMounted(() => {
	dashboard.reload()
})

const studentInfo = computed(() => dashboard.data?.student_info || {})
const stats = computed(() => dashboard.data?.stats || {
	total_enrolled: 0,
	in_progress: 0,
	completed: 0,
	overall_progress: 0,
	certificates_count: 0,
	streak: 0,
})

const continueCourse = computed(() => dashboard.data?.continue_learning || null)
const enrolledCourses = computed(() => dashboard.data?.enrolled_courses || [])
const availableCourses = computed(() => dashboard.data?.available_courses || [])
const recommendedCourses = computed(() => dashboard.data?.recommended_courses || [])
const recentNotifications = computed(() => dashboard.data?.recent_notifications || [])
const recentLessons = computed(() => dashboard.data?.recent_lessons || [])
const certificates = computed(() => dashboard.data?.certificates || [])
const liveClasses = computed(() => {
	if (props.myLiveClasses?.data?.length) return props.myLiveClasses.data
	return dashboard.data?.upcoming_live_classes || []
})

const filteredCourses = computed(() => {
	const courses = enrolledCourses.value
	if (courseFilter.value === 'in_progress') {
		return courses.filter((c) => !c.is_completed)
	}
	if (courseFilter.value === 'completed') {
		return courses.filter((c) => c.is_completed)
	}
	return courses
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
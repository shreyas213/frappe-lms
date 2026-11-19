<template>
	<div class="p-6 max-w-6xl mx-auto space-y-6">
		<!-- Top Bar: Course Title & Stats & Global Actions -->
		<div class="bg-[#1C1C1C] border border-[#2E2E2E] rounded-xl p-5 shadow-sm">
			<div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div class="space-y-1">
					<div class="flex items-center gap-3">
						<h1 class="text-2xl font-bold text-white tracking-tight">
							{{ playlist.data?.course?.title || currentCourseTitle || __('Video Playlist Manager') }}
						</h1>
						<Badge
							:variant="'subtle'"
							:theme="playlist.data?.course?.published ? 'green' : 'amber'"
							size="lg"
						>
							{{ playlist.data?.course?.published ? __('Published') : __('Draft') }}
						</Badge>
					</div>
					<p class="text-sm text-gray-400 line-clamp-1">
						{{ playlist.data?.course?.short_introduction || __('Organize course chapters, video lessons, and attachments.') }}
					</p>
				</div>

				<div class="flex flex-wrap items-center gap-2.5">
					<Button
						variant="subtle"
						:theme="playlist.data?.course?.published ? 'red' : 'gray'"
						:loading="togglingPublish"
						@click="togglePublish"
						class="text-xs"
					>
						{{ playlist.data?.course?.published ? __('Unpublish Course') : __('Publish Course') }}
					</Button>
					<Button
						variant="outline"
						class="!border-[#333333] hover:!bg-[#262626] text-white text-xs"
						@click="openAddChapterModal"
					>
						<template #prefix>
							<span class="lucide-folder-plus size-4 text-[#FF6B00]" />
						</template>
						{{ __('Add Module') }}
					</Button>
					<Button
						variant="solid"
						class="!bg-[#FF6B00] hover:!bg-[#e05e00] text-white text-xs font-semibold"
						@click="openAddLessonModal()"
					>
						<template #prefix>
							<span class="lucide-video size-4" />
						</template>
						{{ __('Add Video Lesson') }}
					</Button>
				</div>
			</div>

			<!-- Stats Row -->
			<div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-5 border-t border-[#2A2A2A]">
				<div class="bg-[#141414] rounded-lg p-3 border border-[#262626]">
					<div class="text-xs text-gray-400 font-medium">{{ __('Total Modules') }}</div>
					<div class="text-2xl font-bold text-white mt-1">{{ totalModulesCount }}</div>
				</div>
				<div class="bg-[#141414] rounded-lg p-3 border border-[#262626]">
					<div class="text-xs text-gray-400 font-medium">{{ __('Total Videos / Lessons') }}</div>
					<div class="text-2xl font-bold text-[#FF6B00] mt-1">{{ totalLessonsCount }}</div>
				</div>
				<div class="bg-[#141414] rounded-lg p-3 border border-[#262626]">
					<div class="text-xs text-gray-400 font-medium">{{ __('Course Duration') }}</div>
					<div class="text-2xl font-bold text-white mt-1">{{ totalDurationString }}</div>
				</div>
				<div class="bg-[#141414] rounded-lg p-3 border border-[#262626]">
					<div class="text-xs text-gray-400 font-medium">{{ __('Status') }}</div>
					<div class="text-2xl font-bold" :class="playlist.data?.course?.published ? 'text-emerald-400' : 'text-amber-400'">
						{{ playlist.data?.course?.published ? __('Live') : __('Draft') }}
					</div>
				</div>
			</div>
		</div>

		<!-- Loading State -->
		<div v-if="playlist.loading && !playlist.data" class="py-12 text-center text-gray-400">
			<div class="inline-block animate-spin size-6 border-2 border-[#FF6B00] border-t-transparent rounded-full mb-2"></div>
			<div>{{ __('Loading video playlist...') }}</div>
		</div>

		<!-- Empty State: No Chapters -->
		<div
			v-else-if="!playlist.data?.chapters?.length"
			class="bg-[#1C1C1C] border border-dashed border-[#333333] rounded-xl p-12 text-center space-y-4"
		>
			<div class="size-14 mx-auto rounded-full bg-[#262626] flex items-center justify-center text-[#FF6B00]">
				<span class="lucide-film size-7" />
			</div>
			<div>
				<h3 class="text-lg font-semibold text-white">{{ __('No modules or video lessons yet') }}</h3>
				<p class="text-sm text-gray-400 max-w-md mx-auto mt-1">
					{{ __('Start building your course video playlist by adding your first module or uploading video lessons.') }}
				</p>
			</div>
			<div class="flex items-center justify-center gap-3 pt-2">
				<Button
					variant="solid"
					class="!bg-[#FF6B00] hover:!bg-[#e05e00] text-white font-medium"
					@click="openAddChapterModal"
				>
					<template #prefix>
						<span class="lucide-folder-plus size-4" />
					</template>
					{{ __('Create First Module') }}
				</Button>
			</div>
		</div>

		<!-- Modules & Lessons Playlist Tree -->
		<div v-else class="space-y-5">
			<div
				v-for="(chapter, chIdx) in playlist.data.chapters"
				:key="chapter.name"
				class="bg-[#1C1C1C] border border-[#2E2E2E] rounded-xl overflow-hidden shadow-sm"
			>
				<!-- Chapter Header -->
				<div class="px-5 py-4 bg-[#212121] border-b border-[#2A2A2A] flex flex-wrap items-center justify-between gap-3">
					<div class="flex items-center gap-3">
						<span class="size-7 rounded-md bg-[#2B2B2B] text-[#FF6B00] font-bold text-xs flex items-center justify-center border border-[#3A3A3A]">
							{{ chIdx + 1 }}
						</span>
						<div>
							<h3 class="text-base font-semibold text-white">
								{{ chapter.title }}
							</h3>
							<p v-if="chapter.description" class="text-xs text-gray-400 mt-0.5 line-clamp-1">
								{{ chapter.description }}
							</p>
						</div>
						<Badge variant="subtle" theme="gray" size="sm">
							{{ chapter.lessons?.length || 0 }} {{ __('videos') }}
						</Badge>
					</div>

					<div class="flex items-center gap-2">
						<Button
							size="sm"
							variant="subtle"
							class="text-xs !bg-[#2A2A2A] text-gray-200 hover:text-white"
							@click="openAddLessonModal(chapter.name)"
						>
							<template #prefix>
								<span class="lucide-plus size-3.5 text-[#FF6B00]" />
							</template>
							{{ __('Add Video') }}
						</Button>
						<Button
							size="sm"
							variant="ghost"
							class="text-xs text-gray-400 hover:text-red-400"
							@click="deleteChapter(chapter.name)"
						>
							<span class="lucide-trash-2 size-3.5" />
						</Button>
					</div>
				</div>

				<!-- Lessons in Chapter -->
				<div class="p-4 space-y-2.5">
					<div
						v-if="!chapter.lessons?.length"
						class="py-6 text-center text-xs text-gray-500 border border-dashed border-[#2A2A2A] rounded-lg space-y-2"
					>
						<div>{{ __('No video lessons in this module yet.') }}</div>
						<Button
							size="sm"
							variant="subtle"
							class="text-xs !bg-[#FF6B00]/10 !text-[#FF6B00] hover:!bg-[#FF6B00]/20"
							@click="openAddLessonModal(chapter.name)"
						>
							<template #prefix>
								<span class="lucide-plus size-3.5" />
							</template>
							{{ __('Add Video to this Module') }}
						</Button>
					</div>

					<div
						v-for="(lesson, lIdx) in chapter.lessons"
						:key="lesson.name"
						class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-lg bg-[#161616] border border-[#262626] hover:border-[#383838] transition-colors"
					>
						<!-- Left: Index + Icon + Title + Description -->
						<div class="flex items-start gap-3 min-w-0">
							<div class="flex items-center gap-2 pt-0.5 shrink-0">
								<span class="text-xs font-semibold text-gray-500 w-6 tabular-nums">
									{{ chIdx + 1 }}.{{ lIdx + 1 }}
								</span>
								<div class="size-8 rounded-lg flex items-center justify-center shrink-0"
									:class="{
										'bg-red-950/60 text-red-400 border border-red-900/50': lesson.youtube,
										'bg-blue-950/60 text-blue-400 border border-blue-900/50': lesson.vimeo_url,
										'bg-purple-950/60 text-purple-400 border border-purple-900/50': lesson.video_file,
										'bg-zinc-800 text-gray-400': !lesson.has_video,
									}"
								>
									<span v-if="lesson.youtube" class="lucide-youtube size-4" />
									<span v-else-if="lesson.vimeo_url" class="lucide-video size-4" />
									<span v-else-if="lesson.video_file" class="lucide-film size-4" />
									<span v-else class="lucide-file-text size-4" />
								</div>
							</div>

							<div class="min-w-0">
								<div class="flex flex-wrap items-center gap-2">
									<h4 class="text-sm font-medium text-white truncate max-w-sm sm:max-w-md">
										{{ lesson.title }}
									</h4>
									<Badge
										v-if="lesson.include_in_preview"
										theme="green"
										size="sm"
									>
										{{ __('Free Preview') }}
									</Badge>
									<Badge
										v-if="!lesson.is_published"
										theme="amber"
										size="sm"
									>
										{{ __('Draft') }}
									</Badge>
									<span
										v-if="lesson.duration"
										class="text-[11px] font-mono text-gray-400 bg-[#222222] px-2 py-0.5 rounded border border-[#303030]"
									>
										{{ lesson.duration }}
									</span>
									<span
										v-if="lesson.attachment"
										class="inline-flex items-center gap-1 text-[11px] text-[#FF6B00] bg-[#FF6B00]/10 px-2 py-0.5 rounded border border-[#FF6B00]/20"
									>
										<span class="lucide-paperclip size-3" />
										{{ __('PDF Notes') }}
									</span>
								</div>

								<p v-if="lesson.description" class="text-xs text-gray-400 line-clamp-1 mt-0.5">
									{{ lesson.description }}
								</p>
							</div>
						</div>

						<!-- Right: Move & Action Buttons -->
						<div class="flex items-center gap-1.5 self-end sm:self-center shrink-0">
							<!-- Reorder buttons -->
							<Button
								size="sm"
								variant="ghost"
								class="!size-7 !p-0 text-gray-400 hover:text-white"
								:disabled="lIdx === 0"
								@click="moveLesson(chapter, lIdx, -1)"
								:tooltip="__('Move Up')"
							>
								<span class="lucide-chevron-up size-4" />
							</Button>
							<Button
								size="sm"
								variant="ghost"
								class="!size-7 !p-0 text-gray-400 hover:text-white"
								:disabled="lIdx === (chapter.lessons?.length || 0) - 1"
								@click="moveLesson(chapter, lIdx, 1)"
								:tooltip="__('Move Down')"
							>
								<span class="lucide-chevron-down size-4" />
							</Button>

							<!-- Edit button -->
							<Button
								size="sm"
								variant="subtle"
								class="text-xs !bg-[#242424] text-gray-300 hover:text-white"
								@click="openEditLessonModal(chapter.name, lesson)"
							>
								<template #prefix>
									<span class="lucide-pencil size-3" />
								</template>
								{{ __('Edit') }}
							</Button>

							<!-- Delete button -->
							<Button
								size="sm"
								variant="ghost"
								class="!size-8 !p-0 text-gray-400 hover:text-red-400"
								@click="deleteLesson(lesson.name)"
								:tooltip="__('Delete Lesson')"
							>
								<span class="lucide-trash-2 size-3.5" />
							</Button>
						</div>
					</div>

					<!-- Add Video in Module Footer -->
					<div v-if="chapter.lessons?.length" class="pt-1">
						<button
							@click="openAddLessonModal(chapter.name)"
							class="w-full py-2 border border-dashed border-[#2E2E2E] hover:border-[#FF6B00] rounded-lg text-xs text-gray-400 hover:text-[#FF6B00] flex items-center justify-center gap-1.5 transition-colors"
						>
							<span class="lucide-plus size-3.5" />
							<span>{{ __('Add another video to') }} {{ chapter.title }}</span>
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- MODAL: Add / Edit Video Lesson (Teleport to body ensures 100% reliable visibility) -->
		<Teleport to="body">
			<div
				v-if="lessonModalOpen"
				class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto"
				@click.self="closeLessonModal"
			>
				<div class="relative w-full max-w-2xl bg-[#1C1C1C] border border-[#333333] rounded-2xl p-6 shadow-2xl text-white space-y-4 my-8">
					<!-- Header -->
					<div class="flex items-center justify-between pb-3 border-b border-[#2C2C2C]">
						<h3 class="text-lg font-bold text-white flex items-center gap-2">
							<span class="lucide-video size-5 text-[#FF6B00]" />
							{{ editingLessonName ? __('Edit Video Lesson') : __('Add Video Lesson') }}
						</h3>
						<button
							type="button"
							@click="closeLessonModal"
							class="text-gray-400 hover:text-white p-1 rounded-lg hover:bg-[#2A2A2A] transition-colors"
						>
							<span class="lucide-x size-5" />
						</button>
					</div>

					<!-- Form Content -->
					<form @submit.prevent="saveLesson" class="space-y-4">
						<!-- Target Module -->
						<div>
							<label class="block text-xs font-semibold text-gray-300 mb-1.5">
								{{ __('Target Module / Chapter') }} <span class="text-red-400">*</span>
							</label>
							<select
								v-model="lessonForm.chapter"
								class="w-full bg-[#181818] border border-[#333333] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-[#FF6B00]"
								required
							>
								<option
									v-for="ch in playlist.data?.chapters || []"
									:key="ch.name"
									:value="ch.name"
								>
									{{ ch.title }}
								</option>
							</select>
						</div>

						<!-- Lesson Title -->
						<div>
							<label class="block text-xs font-semibold text-gray-300 mb-1.5">
								{{ __('Lesson Title') }} <span class="text-red-400">*</span>
							</label>
							<input
								type="text"
								v-model="lessonForm.title"
								:placeholder="__('e.g. Masterclass Lesson 1: Introduction to Setup')"
								class="w-full bg-[#181818] border border-[#333333] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#FF6B00]"
								required
							/>
						</div>

						<!-- Description -->
						<div>
							<label class="block text-xs font-semibold text-gray-300 mb-1.5">
								{{ __('Lesson Description') }}
							</label>
							<textarea
								v-model="lessonForm.description"
								rows="2"
								:placeholder="__('Short summary of what is covered in this video lesson...')"
								class="w-full bg-[#181818] border border-[#333333] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#FF6B00]"
							></textarea>
						</div>

						<!-- Video Source Selector -->
						<div class="border border-[#2D2D2D] rounded-xl p-3 bg-[#151515] space-y-3">
							<div class="flex items-center gap-2 border-b border-[#262626] pb-2">
								<button
									type="button"
									@click="videoSourceType = 'youtube'"
									class="px-3 py-1 rounded text-xs font-medium transition-colors"
									:class="videoSourceType === 'youtube' ? 'bg-red-600/20 text-red-400 border border-red-500/30' : 'text-gray-400 hover:text-white'"
								>
									{{ __('YouTube URL') }}
								</button>
								<button
									type="button"
									@click="videoSourceType = 'vimeo'"
									class="px-3 py-1 rounded text-xs font-medium transition-colors"
									:class="videoSourceType === 'vimeo' ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' : 'text-gray-400 hover:text-white'"
								>
									{{ __('Vimeo URL') }}
								</button>
								<button
									type="button"
									@click="videoSourceType = 'upload'"
									class="px-3 py-1 rounded text-xs font-medium transition-colors"
									:class="videoSourceType === 'upload' ? 'bg-[#FF6B00]/20 text-[#FF6B00] border border-[#FF6B00]/30' : 'text-gray-400 hover:text-white'"
								>
									{{ __('Upload MP4 File') }}
								</button>
							</div>

							<!-- YouTube Field -->
							<div v-if="videoSourceType === 'youtube'">
								<label class="block text-xs text-gray-300 mb-1">{{ __('YouTube Video URL') }}</label>
								<input
									type="url"
									v-model="lessonForm.youtube"
									placeholder="https://www.youtube.com/watch?v=..."
									class="w-full bg-[#1C1C1C] border border-[#333333] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#FF6B00]"
								/>
							</div>

							<!-- Vimeo Field -->
							<div v-else-if="videoSourceType === 'vimeo'">
								<label class="block text-xs text-gray-300 mb-1">{{ __('Vimeo Video URL') }}</label>
								<input
									type="url"
									v-model="lessonForm.vimeo_url"
									placeholder="https://vimeo.com/123456789"
									class="w-full bg-[#1C1C1C] border border-[#333333] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#FF6B00]"
								/>
							</div>

							<!-- Direct MP4 Large Video Upload Field -->
							<div v-else-if="videoSourceType === 'upload'" class="space-y-3">
								<div class="flex items-center justify-between">
									<label class="block text-xs font-semibold text-gray-300">
										{{ __('Upload MP4 Video (100MB, 250MB, 500MB, 1GB, 2GB+)') }}
									</label>
									<span class="text-[11px] text-gray-400">
										{{ __('Max limit:') }} {{ maxUploadSizeMb }} MB
									</span>
								</div>

								<!-- Input row with URL field & Browse button -->
								<div class="flex items-center gap-2">
									<input
										type="text"
										v-model="lessonForm.video_file"
										placeholder="/files/lesson_video.mp4 or https://..."
										:disabled="videoUpload.uploading || videoUpload.assembling"
										class="flex-1 bg-[#1C1C1C] border border-[#333333] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#FF6B00] disabled:opacity-50"
									/>
									<label
										class="px-3.5 py-2 rounded-lg border text-xs font-semibold shrink-0 transition-colors flex items-center gap-1.5"
										:class="videoUpload.uploading || videoUpload.assembling
											? 'bg-[#222222] text-gray-500 border-[#333333] cursor-not-allowed'
											: 'bg-[#FF6B00] hover:bg-[#e05e00] text-white border-[#FF6B00] cursor-pointer shadow-sm'"
									>
										<span class="lucide-upload size-3.5" />
										<span>{{ videoUpload.uploading ? __('Uploading...') : __('Browse MP4') }}</span>
										<input
											type="file"
											accept="video/mp4,video/quicktime,video/webm,video/x-m4v,video/*"
											class="hidden"
											:disabled="videoUpload.uploading || videoUpload.assembling"
											@change="handleVideoFileSelected"
										/>
									</label>
								</div>

								<!-- Active Large File Upload Card -->
								<div
									v-if="videoUpload.active"
									class="p-3.5 rounded-xl border bg-[#141414] transition-all space-y-2.5"
									:class="{
										'border-[#FF6B00]/40': videoUpload.uploading || videoUpload.assembling,
										'border-emerald-500/40 bg-emerald-950/10': videoUpload.success,
										'border-red-500/40 bg-red-950/10': videoUpload.error,
									}"
								>
									<!-- Info Row: File name, sizes, speed, cancel button -->
									<div class="flex items-center justify-between text-xs">
										<div class="flex items-center gap-2 min-w-0 pr-2">
											<span
												class="size-7 rounded-lg flex items-center justify-center shrink-0"
												:class="{
													'bg-[#FF6B00]/20 text-[#FF6B00]': videoUpload.uploading,
													'bg-blue-500/20 text-blue-400': videoUpload.assembling,
													'bg-emerald-500/20 text-emerald-400': videoUpload.success,
													'bg-red-500/20 text-red-400': videoUpload.error,
												}"
											>
												<span v-if="videoUpload.uploading" class="lucide-film size-4 animate-pulse" />
												<span v-else-if="videoUpload.assembling" class="lucide-loader-2 size-4 animate-spin" />
												<span v-else-if="videoUpload.success" class="lucide-check-circle size-4" />
												<span v-else class="lucide-alert-circle size-4" />
											</span>
											<div class="min-w-0">
												<div class="font-medium text-white truncate max-w-xs sm:max-w-md">
													{{ videoUpload.fileName }}
												</div>
												<div class="text-[11px] text-gray-400">
													{{ formatBytes(videoUpload.fileSize) }}
													<span v-if="videoUpload.speedString && videoUpload.uploading">
														• {{ videoUpload.speedString }}
													</span>
													<span v-if="videoUpload.uploading && videoUpload.totalChunks > 1">
														• {{ __('Chunk') }} {{ videoUpload.currentChunk }} / {{ videoUpload.totalChunks }}
													</span>
												</div>
											</div>
										</div>

										<div class="flex items-center gap-2 shrink-0">
											<span
												v-if="videoUpload.uploading"
												class="text-xs font-mono font-bold text-[#FF6B00]"
											>
												{{ videoUpload.progressPercent }}%
											</span>
											<span
												v-else-if="videoUpload.assembling"
												class="text-xs font-medium text-blue-400 flex items-center gap-1"
											>
												<span class="inline-block size-3 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
												{{ __('Assembling...') }}
											</span>
											<Button
												v-if="videoUpload.uploading"
												size="sm"
												variant="ghost"
												class="text-xs text-red-400 hover:text-red-300 hover:bg-red-950/40 !h-7 !px-2"
												@click="cancelVideoUpload"
											>
												{{ __('Cancel') }}
											</Button>
										</div>
									</div>

									<!-- Real Upload Progress Bar -->
									<div
										v-if="videoUpload.uploading || videoUpload.assembling"
										class="w-full bg-[#262626] rounded-full h-2 overflow-hidden border border-[#333333]"
									>
										<div
											class="h-full bg-gradient-to-r from-[#FF6B00] to-[#FFA040] transition-all duration-200"
											:class="{ 'animate-pulse': videoUpload.assembling }"
											:style="{ width: `${videoUpload.progressPercent}%` }"
										></div>
									</div>

									<!-- Status & Feedback Details -->
									<div class="text-xs">
										<p v-if="videoUpload.uploading" class="text-gray-400">
											{{ __('Uploaded:') }} {{ formatBytes(videoUpload.uploadedBytes) }} / {{ formatBytes(videoUpload.fileSize) }}
											({{ videoUpload.progressPercent }}%)
										</p>
										<p v-else-if="videoUpload.assembling" class="text-blue-400">
											{{ __('Upload chunks complete! Assembling & validating MP4 video stream on server...') }}
										</p>
										<p v-else-if="videoUpload.success" class="text-emerald-400 flex items-center gap-1.5 font-medium">
											<span class="lucide-check size-3.5" />
											{{ __('Video uploaded and verified successfully in Frappe storage!') }}
										</p>
										<div v-else-if="videoUpload.error" class="text-red-400 flex items-center justify-between gap-2">
											<span class="truncate">{{ videoUpload.error }}</span>
											<button
												type="button"
												@click="videoUpload.active = false"
												class="text-[11px] underline hover:text-red-300 shrink-0"
											>
												{{ __('Dismiss') }}
											</button>
										</div>
									</div>
								</div>

								<!-- Existing video indicator -->
								<div
									v-if="lessonForm.video_file && !videoUpload.active"
									class="p-2.5 rounded-lg bg-[#181818] border border-[#2B2B2B] flex items-center justify-between text-xs text-gray-300"
								>
									<div class="flex items-center gap-2 truncate">
										<span class="lucide-video size-4 text-[#FF6B00] shrink-0" />
										<span class="truncate font-mono text-[11px]">{{ lessonForm.video_file }}</span>
									</div>
									<Badge theme="green" size="sm" class="shrink-0">{{ __('Attached') }}</Badge>
								</div>
							</div>
						</div>

						<!-- Duration, PDF Attachment, and Lesson Order in 3 columns -->
						<div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
							<!-- Duration -->
							<div>
								<label class="block text-xs font-semibold text-gray-300 mb-1.5">
									{{ __('Video Duration') }}
								</label>
								<input
									type="text"
									v-model="lessonForm.duration"
									:placeholder="__('e.g. 14:35 or 20 mins')"
									class="w-full bg-[#181818] border border-[#333333] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#FF6B00]"
								/>
							</div>

							<!-- Lesson Order -->
							<div>
								<label class="block text-xs font-semibold text-gray-300 mb-1.5">
									{{ __('Lesson Order (Idx)') }}
								</label>
								<input
									type="number"
									min="1"
									v-model.number="lessonForm.idx"
									:placeholder="__('e.g. 1')"
									class="w-full bg-[#181818] border border-[#333333] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#FF6B00]"
								/>
							</div>

							<!-- PDF Notes Attachment -->
							<div>
								<label class="block text-xs font-semibold text-gray-300 mb-1.5">
									{{ __('PDF Notes / Attachment') }}
								</label>
								<div class="flex items-center gap-1.5">
									<input
										type="text"
										v-model="lessonForm.attachment"
										:placeholder="__('/files/notes.pdf')"
										class="flex-1 min-w-0 bg-[#181818] border border-[#333333] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#FF6B00]"
									/>
									<label class="px-2.5 py-2 rounded-lg bg-[#282828] hover:bg-[#333333] border border-[#404040] text-xs font-semibold text-white cursor-pointer shrink-0">
										<span v-if="uploadingPdf">{{ __('...') }}</span>
										<span v-else>{{ __('PDF') }}</span>
										<input
											type="file"
											accept=".pdf,.doc,.docx"
											class="hidden"
											:disabled="uploadingPdf"
											@change="handlePdfUpload"
										/>
									</label>
								</div>
							</div>
						</div>

						<!-- Options: Preview & Publish -->
						<div class="flex flex-wrap items-center gap-6 pt-2">
							<label class="flex items-center gap-2 cursor-pointer">
								<input
									type="checkbox"
									v-model="lessonForm.include_in_preview"
									class="size-4 rounded accent-[#FF6B00] bg-[#1C1C1C] border-[#404040]"
								/>
								<span class="text-xs text-gray-300 font-medium">
									{{ __('Free Preview (accessible before enrollment)') }}
								</span>
							</label>

							<label class="flex items-center gap-2 cursor-pointer">
								<input
									type="checkbox"
									v-model="lessonForm.is_published"
									class="size-4 rounded accent-[#FF6B00] bg-[#1C1C1C] border-[#404040]"
								/>
								<span class="text-xs text-gray-300 font-medium">
									{{ __('Published') }}
								</span>
							</label>
						</div>

						<!-- Action Buttons -->
						<div class="flex items-center justify-end gap-3 pt-4 border-t border-[#2A2A2A]">
							<Button
								type="button"
								variant="subtle"
								:disabled="videoUpload.uploading || videoUpload.assembling"
								@click="closeLessonModal"
							>
								{{ __('Cancel') }}
							</Button>
							<Button
								type="submit"
								variant="solid"
								:loading="savingLesson"
								:disabled="videoUpload.uploading || videoUpload.assembling"
								class="!bg-[#FF6B00] hover:!bg-[#e05e00] text-white font-semibold disabled:opacity-50"
							>
								{{ editingLessonName ? __('Update Lesson') : __('Save Video Lesson') }}
							</Button>
						</div>
					</form>
				</div>
			</div>
		</Teleport>

		<!-- MODAL: Add Module / Chapter (Teleport to body) -->
		<Teleport to="body">
			<div
				v-if="chapterModalOpen"
				class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
				@click.self="chapterModalOpen = false"
			>
				<div class="relative w-full max-w-md bg-[#1C1C1C] border border-[#333333] rounded-2xl p-6 shadow-2xl text-white space-y-4">
					<div class="flex items-center justify-between pb-3 border-b border-[#2C2C2C]">
						<h3 class="text-lg font-bold text-white flex items-center gap-2">
							<span class="lucide-folder-plus size-5 text-[#FF6B00]" />
							{{ __('Create New Module / Chapter') }}
						</h3>
						<button
							type="button"
							@click="chapterModalOpen = false"
							class="text-gray-400 hover:text-white p-1 rounded-lg hover:bg-[#2A2A2A] transition-colors"
						>
							<span class="lucide-x size-5" />
						</button>
					</div>

					<form @submit.prevent="saveChapter" class="space-y-4">
						<div>
							<label class="block text-xs font-semibold text-gray-300 mb-1.5">
								{{ __('Module Title') }} <span class="text-red-400">*</span>
							</label>
							<input
								type="text"
								v-model="newChapterTitle"
								:placeholder="__('e.g. Module 1: Foundational Core')"
								class="w-full bg-[#181818] border border-[#333333] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#FF6B00]"
								required
								autofocus
							/>
						</div>

						<div>
							<label class="block text-xs font-semibold text-gray-300 mb-1.5">
								{{ __('Module Description') }}
							</label>
							<textarea
								v-model="newChapterDescription"
								rows="2"
								:placeholder="__('Short summary of topics in this module...')"
								class="w-full bg-[#181818] border border-[#333333] rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-[#FF6B00]"
							></textarea>
						</div>

						<div class="flex items-center justify-end gap-3 pt-3 border-t border-[#2A2A2A]">
							<Button
								type="button"
								variant="subtle"
								@click="chapterModalOpen = false"
							>
								{{ __('Cancel') }}
							</Button>
							<Button
								type="submit"
								variant="solid"
								:loading="savingChapter"
								class="!bg-[#FF6B00] hover:!bg-[#e05e00] text-white font-semibold"
							>
								{{ __('Save Module') }}
							</Button>
						</div>
					</form>
				</div>
			</div>
		</Teleport>
	</div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Badge, Button, call, createResource, toast } from 'frappe-ui'
import type { CourseDetails, Resource } from '@/types'

const props = defineProps<{
	course?: Resource<CourseDetails | null>
}>()

const route = useRoute()

// Resilient Course Name resolution
const courseName = computed(() => {
	if (props.course?.data?.name) return props.course.data.name
	if ((props.course as any)?.name) return (props.course as any).name
	if (route.params.courseName) return String(route.params.courseName)
	return ''
})

const currentCourseTitle = computed(() => {
	return props.course?.data?.title || (playlist.data?.course?.title ?? '')
})

// Playlist Resource
const playlist = createResource({
	url: 'lms.lms.api.get_course_playlist',
	makeParams() {
		return { course: courseName.value }
	},
	auto: Boolean(courseName.value),
})

watch(
	courseName,
	(newVal) => {
		if (newVal) playlist.reload()
	},
	{ immediate: true }
)

const totalModulesCount = computed(() => {
	return playlist.data?.chapters?.length || 0
})

const totalLessonsCount = computed(() => {
	const chapters = playlist.data?.chapters || []
	return chapters.reduce((acc: number, c: any) => acc + (c.lessons?.length || 0), 0)
})

const totalDurationString = computed(() => {
	const chapters = playlist.data?.chapters || []
	let totalMinutes = 0
	chapters.forEach((c: any) => {
		(c.lessons || []).forEach((l: any) => {
			if (l.duration) {
				const parts = String(l.duration).split(':')
				if (parts.length === 2) {
					totalMinutes += parseInt(parts[0], 10) || 0
				} else {
					const num = parseInt(l.duration, 10)
					if (!isNaN(num)) totalMinutes += num
				}
			}
		})
	})
	if (totalMinutes === 0) return 'Self-paced'
	const hrs = Math.floor(totalMinutes / 60)
	const mins = totalMinutes % 60
	return hrs > 0 ? `${hrs}h ${mins}m` : `${mins} mins`
})

// Publish Toggle
const togglingPublish = ref(false)
const togglePublish = async () => {
	if (!courseName.value) return
	togglingPublish.value = true
	const currentStatus = playlist.data?.course?.published ? 1 : 0
	const newStatus = currentStatus ? 0 : 1
	try {
		await call('lms.lms.api.toggle_course_publish_status', {
			course: courseName.value,
			publish: newStatus,
		})
		toast.success(newStatus ? __('Course published successfully!') : __('Course saved as draft.'))
		playlist.reload()
		props.course?.reload?.()
	} catch (err) {
		console.error(err)
		toast.error(__('Failed to update course status'))
	} finally {
		togglingPublish.value = false
	}
}

// Chapter Modal State
const chapterModalOpen = ref(false)
const newChapterTitle = ref('')
const newChapterDescription = ref('')
const savingChapter = ref(false)

const openAddChapterModal = () => {
	newChapterTitle.value = `Module ${(playlist.data?.chapters?.length || 0) + 1}`
	newChapterDescription.value = ''
	chapterModalOpen.value = true
}

const saveChapter = async () => {
	const title = newChapterTitle.value.trim()
	if (!title) {
		toast.error(__('Please enter a module title'))
		return
	}
	if (!courseName.value) {
		toast.error(__('Course not identified'))
		return
	}

	savingChapter.value = true
	try {
		const res = await call('lms.lms.api.create_course_chapter', {
			course: courseName.value,
			title: title,
			description: newChapterDescription.value.trim() || undefined,
		})
		if (res && res.status === 'success') {
			toast.success(__('Module created successfully!'))
			chapterModalOpen.value = false
			newChapterTitle.value = ''
			newChapterDescription.value = ''
			await playlist.reload()
			props.course?.reload?.()
		}
	} catch (err: any) {
		console.error(err)
		toast.error(err?.message || __('Could not create module'))
	} finally {
		savingChapter.value = false
	}
}

const deleteChapter = async (chapterName: string) => {
	if (!confirm(__('Are you sure you want to delete this module and all its lessons?'))) return
	try {
		await call('lms.lms.api.delete_chapter', { chapter: chapterName })
		toast.success(__('Module deleted'))
		playlist.reload()
		props.course?.reload?.()
	} catch (e) {
		console.error(e)
		toast.error(__('Could not delete chapter'))
	}
}

// Lesson Modal State
const lessonModalOpen = ref(false)
const editingLessonName = ref<string | null>(null)
const videoSourceType = ref<'youtube' | 'vimeo' | 'upload'>('youtube')
const uploadingVideo = ref(false)
const uploadingPdf = ref(false)
const savingLesson = ref(false)
const maxUploadSizeMb = ref(2048)

const fetchUploadConfig = async () => {
	try {
		const res = await call('lms.lms.api.get_video_upload_config')
		if (res && res.max_size_mb) {
			maxUploadSizeMb.value = res.max_size_mb
		}
	} catch (e) {
		console.error(e)
	}
}

const formatBytes = (bytes: number): string => {
	if (!bytes || bytes <= 0) return '0 B'
	if (bytes < 1024) return bytes + ' B'
	if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
	if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
	return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
}

const videoUpload = reactive({
	active: false,
	uploading: false,
	assembling: false,
	error: null as string | null,
	success: false,
	fileName: '',
	fileSize: 0,
	uploadedBytes: 0,
	progressPercent: 0,
	currentChunk: 0,
	totalChunks: 0,
	speedString: '',
	uploadId: null as string | null,
	xhr: null as XMLHttpRequest | null,
	aborted: false,
})

const cancelVideoUpload = async () => {
	if (!videoUpload.uploading && !videoUpload.assembling) return
	videoUpload.aborted = true
	if (videoUpload.xhr) {
		videoUpload.xhr.abort()
		videoUpload.xhr = null
	}
	if (videoUpload.uploadId) {
		try {
			await call('lms.lms.api.cancel_video_upload', { upload_id: videoUpload.uploadId })
		} catch (e) {
			console.error(e)
		}
	}
	videoUpload.uploading = false
	videoUpload.assembling = false
	videoUpload.error = __('Upload cancelled')
	toast.info(__('Upload cancelled'))
}

const closeLessonModal = () => {
	if (videoUpload.uploading || videoUpload.assembling) {
		if (!confirm(__('A video upload is currently in progress. Cancel upload and close?'))) {
			return
		}
		cancelVideoUpload()
	}
	lessonModalOpen.value = false
}

const lessonForm = reactive({
	chapter: '',
	title: '',
	description: '',
	youtube: '',
	vimeo_url: '',
	video_file: '',
	duration: '',
	attachment: '',
	idx: 1,
	include_in_preview: false,
	is_published: true,
})

const openAddLessonModal = (chapterName?: string) => {
	editingLessonName.value = null
	lessonForm.chapter = chapterName || playlist.data?.chapters?.[0]?.name || ''
	
	// Determine default index
	const targetChapter = playlist.data?.chapters?.find((c: any) => c.name === lessonForm.chapter)
	lessonForm.idx = (targetChapter?.lessons?.length || 0) + 1

	lessonForm.title = ''
	lessonForm.description = ''
	lessonForm.youtube = ''
	lessonForm.vimeo_url = ''
	lessonForm.video_file = ''
	lessonForm.duration = ''
	lessonForm.attachment = ''
	lessonForm.include_in_preview = false
	lessonForm.is_published = true
	videoSourceType.value = 'youtube'

	videoUpload.active = false
	videoUpload.uploading = false
	videoUpload.assembling = false
	videoUpload.error = null
	videoUpload.success = false
	videoUpload.aborted = false
	fetchUploadConfig()

	lessonModalOpen.value = true
}

const openEditLessonModal = (chapterName: string, lesson: any) => {
	editingLessonName.value = lesson.name
	lessonForm.chapter = chapterName
	lessonForm.title = lesson.title
	lessonForm.description = lesson.description || ''
	lessonForm.youtube = lesson.youtube || ''
	lessonForm.vimeo_url = lesson.vimeo_url || ''
	lessonForm.video_file = lesson.video_file || ''
	lessonForm.duration = lesson.duration || ''
	lessonForm.attachment = lesson.attachment || ''
	lessonForm.idx = lesson.idx || 1
	lessonForm.include_in_preview = Boolean(lesson.include_in_preview)
	lessonForm.is_published = lesson.is_published !== 0

	if (lesson.vimeo_url) videoSourceType.value = 'vimeo'
	else if (lesson.video_file) videoSourceType.value = 'upload'
	else videoSourceType.value = 'youtube'

	videoUpload.active = false
	videoUpload.uploading = false
	videoUpload.assembling = false
	videoUpload.error = null
	videoUpload.success = false
	videoUpload.aborted = false
	fetchUploadConfig()

	lessonModalOpen.value = true
}

// Resilient chunked large video upload pipeline
const handleVideoFileSelected = async (event: Event) => {
	const input = event.target as HTMLInputElement
	if (!input.files?.length) return
	const file = input.files[0]

	// Format check
	const lowerName = file.name.toLowerCase()
	const validExts = ['.mp4', '.m4v', '.mov', '.webm', '.mkv']
	if (!validExts.some((ext) => lowerName.endsWith(ext))) {
		toast.error(__('Please select a valid video file (.mp4, .m4v, .mov, .webm)'))
		input.value = ''
		return
	}

	// Size check against server config
	const maxBytes = maxUploadSizeMb.value * 1024 * 1024
	if (file.size > maxBytes) {
		const sizeMb = (file.size / (1024 * 1024)).toFixed(1)
		toast.error(
			__('File size ({0} MB) exceeds maximum allowed limit of {1} MB').replace('{0}', sizeMb).replace('{1}', String(maxUploadSizeMb.value))
		)
		input.value = ''
		return
	}

	const CHUNK_SIZE = 5 * 1024 * 1024 // 5 MB chunks
	const totalChunks = Math.ceil(file.size / CHUNK_SIZE)

	videoUpload.active = true
	videoUpload.uploading = true
	videoUpload.assembling = false
	videoUpload.error = null
	videoUpload.success = false
	videoUpload.aborted = false
	videoUpload.fileName = file.name
	videoUpload.fileSize = file.size
	videoUpload.uploadedBytes = 0
	videoUpload.progressPercent = 0
	videoUpload.currentChunk = 0
	videoUpload.totalChunks = totalChunks
	videoUpload.speedString = ''

	try {
		// Step 1: Initiate upload session on server
		const initRes = await call('lms.lms.api.initiate_video_upload', {
			filename: file.name,
			total_size: file.size,
			total_chunks: totalChunks,
			course: courseName.value || undefined,
			chapter: lessonForm.chapter || undefined,
			lesson: editingLessonName.value || undefined,
			is_private: 0,
		})

		if (!initRes || !initRes.upload_id) {
			throw new Error(__('Failed to initialize upload session on server.'))
		}
		videoUpload.uploadId = initRes.upload_id

		const csrfToken = (window as any).csrf_token || ''
		let lastLoaded = 0
		let lastTime = Date.now()

		// Step 2: Upload chunks sequentially
		for (let i = 0; i < totalChunks; i++) {
			if (videoUpload.aborted) break

			videoUpload.currentChunk = i + 1
			const start = i * CHUNK_SIZE
			const end = Math.min(start + CHUNK_SIZE, file.size)
			const chunkBlob = file.slice(start, end)

			let attempt = 0
			let chunkUploaded = false

			while (attempt < 3 && !chunkUploaded && !videoUpload.aborted) {
				attempt++
				try {
					await new Promise<void>((resolve, reject) => {
						const xhr = new XMLHttpRequest()
						videoUpload.xhr = xhr

						xhr.upload.onprogress = (e) => {
							if (e.lengthComputable) {
								const currentTotalLoaded = start + e.loaded
								videoUpload.uploadedBytes = currentTotalLoaded
								videoUpload.progressPercent = Math.min(
									99,
									Math.round((currentTotalLoaded / file.size) * 100)
								)
								const now = Date.now()
								const elapsed = (now - lastTime) / 1000
								if (elapsed >= 0.5) {
									const diff = currentTotalLoaded - lastLoaded
									const speed = diff / elapsed
									videoUpload.speedString = formatBytes(speed) + '/s'
									lastLoaded = currentTotalLoaded
									lastTime = now
								}
							}
						}

						xhr.onload = () => {
							videoUpload.xhr = null
							if (xhr.status >= 200 && xhr.status < 300) {
								chunkUploaded = true
								resolve()
							} else {
								let errMsg = xhr.statusText
								try {
									const parsed = JSON.parse(xhr.responseText)
									if (parsed._server_messages) {
										const msgs = JSON.parse(parsed._server_messages)
										errMsg = msgs.map((m: any) => JSON.parse(m).message).join(' ')
									} else if (parsed.message) {
										errMsg = parsed.message
									}
								} catch (_) {}
								reject(new Error(errMsg || `Chunk ${i + 1} upload failed (HTTP ${xhr.status})`))
							}
						}

						xhr.onerror = () => {
							videoUpload.xhr = null
							reject(new Error(`Network interruption while uploading chunk ${i + 1}. Retrying...`))
						}

						xhr.onabort = () => {
							videoUpload.xhr = null
							reject(new Error(__('Upload cancelled')))
						}

						const formData = new FormData()
						formData.append('upload_id', videoUpload.uploadId!)
						formData.append('chunk_index', String(i))
						formData.append('chunk', chunkBlob, `chunk_${i}`)

						xhr.open('POST', '/api/method/lms.lms.api.upload_video_chunk')
						if (csrfToken && csrfToken !== 'None') {
							xhr.setRequestHeader('X-Frappe-CSRF-Token', csrfToken)
						}
						xhr.send(formData)
					})
				} catch (err: any) {
					if (videoUpload.aborted) throw err
					if (attempt >= 3) throw err
					await new Promise((r) => setTimeout(r, 1000 * attempt))
				}
			}
		}

		if (videoUpload.aborted) return

		// Step 3: Server Assembly & Verification
		videoUpload.uploading = false
		videoUpload.assembling = true
		videoUpload.progressPercent = 100

		const assemRes = await call('lms.lms.api.assemble_video_upload', {
			upload_id: videoUpload.uploadId,
		})

		if (assemRes && assemRes.file_url) {
			videoUpload.success = true
			lessonForm.video_file = assemRes.file_url
			toast.success(__('Video uploaded and verified successfully!'))
		} else {
			throw new Error(__('Server assembly returned empty file URL.'))
		}
	} catch (err: any) {
		console.error(err)
		videoUpload.error = err.message || __('Large video upload failed')
		toast.error(err.message || __('Large video upload failed'))
	} finally {
		videoUpload.uploading = false
		videoUpload.assembling = false
		input.value = ''
	}
}

// PDF Notes file upload
const uploadFileToFrappe = async (file: File): Promise<string> => {
	const formData = new FormData()
	formData.append('file', file)
	formData.append('is_private', '0')
	formData.append('doctype', 'Course Lesson')

	const csrfToken = (window as any).csrf_token || ''
	const res = await fetch('/api/method/upload_file', {
		method: 'POST',
		body: formData,
		headers: {
			'X-Frappe-CSRF-Token': csrfToken,
		},
	})
	if (!res.ok) {
		const errText = await res.text()
		throw new Error(errText || 'Upload failed')
	}
	const data = await res.json()
	return data.message?.file_url || ''
}

const handlePdfUpload = async (event: Event) => {
	const input = event.target as HTMLInputElement
	if (!input.files?.length) return
	uploadingPdf.value = true
	try {
		const fileUrl = await uploadFileToFrappe(input.files[0])
		lessonForm.attachment = fileUrl
		toast.success(__('PDF attachment uploaded!'))
	} catch (e: any) {
		console.error(e)
		toast.error(__('Failed to upload attachment'))
	} finally {
		uploadingPdf.value = false
	}
}

const saveLesson = async () => {
	if (videoUpload.uploading || videoUpload.assembling) {
		toast.warning(__('Please wait for the video upload to finish before saving.'))
		return
	}

	const title = lessonForm.title.trim()
	if (!title) {
		toast.error(__('Please enter lesson title'))
		return
	}
	if (!lessonForm.chapter) {
		toast.error(__('Please select a module / chapter'))
		return
	}
	if (!courseName.value) {
		toast.error(__('Course not identified'))
		return
	}

	savingLesson.value = true
	try {
		const res = await call('lms.lms.api.quick_add_video_lesson', {
			course: courseName.value,
			chapter: lessonForm.chapter,
			title: title,
			lesson: editingLessonName.value || undefined,
			description: lessonForm.description.trim(),
			video_file: videoSourceType.value === 'upload' ? lessonForm.video_file.trim() : '',
			youtube: videoSourceType.value === 'youtube' ? lessonForm.youtube.trim() : '',
			vimeo_url: videoSourceType.value === 'vimeo' ? lessonForm.vimeo_url.trim() : '',
			duration: lessonForm.duration.trim(),
			attachment: lessonForm.attachment.trim(),
			include_in_preview: lessonForm.include_in_preview ? 1 : 0,
			is_published: lessonForm.is_published ? 1 : 0,
			idx: lessonForm.idx || undefined,
		})

		if (res && res.status === 'success') {
			toast.success(editingLessonName.value ? __('Lesson updated!') : __('Video lesson added!'))
			lessonModalOpen.value = false
			await playlist.reload()
			props.course?.reload?.()
		}
	} catch (e: any) {
		console.error(e)
		toast.error(e?.message || __('Could not save lesson'))
	} finally {
		savingLesson.value = false
	}
}

const deleteLesson = async (lessonName: string) => {
	if (!confirm(__('Are you sure you want to delete this video lesson?'))) return
	try {
		await call('lms.lms.api.delete_video_lesson', { lesson: lessonName })
		toast.success(__('Lesson deleted'))
		playlist.reload()
		props.course?.reload?.()
	} catch (e) {
		console.error(e)
		toast.error(__('Could not delete lesson'))
	}
}

// Reordering inside a chapter
const moveLesson = async (chapter: any, currentIdx: number, delta: number) => {
	const lessons = [...(chapter.lessons || [])]
	const newIdx = currentIdx + delta
	if (newIdx < 0 || newIdx >= lessons.length) return

	// Swap
	const temp = lessons[currentIdx]
	lessons[currentIdx] = lessons[newIdx]
	lessons[newIdx] = temp

	const lessonNames = lessons.map((l: any) => l.name)
	try {
		await call('lms.lms.api.reorder_playlist_lessons', {
			chapter: chapter.name,
			lesson_names: lessonNames,
		})
		playlist.reload()
		props.course?.reload?.()
	} catch (e) {
		console.error(e)
		toast.error(__('Could not reorder lessons'))
	}
}
</script>

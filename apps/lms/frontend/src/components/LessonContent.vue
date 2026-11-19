<template>
	<!-- Direct MP4 Video Player -->
	<div
		v-if="videoFile"
		class="not-prose my-5 overflow-hidden rounded-7 border border-outline-gray-2 bg-black"
	>
		<video
			controls
			width="100%"
			class="block w-full max-h-[600px]"
			controlsList="nodownload"
			oncontextmenu="return false;"
		>
			<source :src="safeUrl(videoFile)" type="video/mp4" />
		</video>
	</div>

	<!-- Vimeo Video Player -->
	<div
		v-else-if="vimeoEmbedUrl(vimeoUrl)"
		class="not-prose my-5 overflow-hidden rounded-7 border border-outline-gray-2 bg-black aspect-video"
	>
		<iframe
			:src="vimeoEmbedUrl(vimeoUrl)"
			width="100%"
			height="100%"
			frameborder="0"
			allow="autoplay; fullscreen; picture-in-picture"
			allowfullscreen
			class="w-full h-full block"
		></iframe>
	</div>

	<!-- YouTube Video Player -->
	<div
		v-else-if="youtubeEmbedId(youtube)"
		:key="youtubeEmbedId(youtube)"
		class="not-prose my-5 overflow-hidden rounded-7 border border-outline-gray-2"
	>
		<div
			class="video-player"
			data-plyr-provider="youtube"
			:data-plyr-embed-id="youtubeEmbedId(youtube)"
		></div>
	</div>

	<!-- Attached PDF / Lesson Notes -->
	<div
		v-if="attachment"
		class="not-prose my-5 flex items-center justify-between rounded-6 border border-outline-gray-2 bg-surface-gray-2 p-4"
	>
		<div class="flex items-center gap-3 min-w-0">
			<span class="lucide-file-text size-6 text-[#FF6B00] shrink-0" />
			<div class="min-w-0">
				<div class="font-medium text-ink-gray-9 truncate">
					{{ __('Lesson PDF Notes & Resources') }}
				</div>
				<div class="text-xs text-ink-gray-5 truncate">
					{{ attachment.split('/').pop() }}
				</div>
			</div>
		</div>
		<a
			:href="attachment"
			target="_blank"
			download
			class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#FF6B00] text-white text-xs font-semibold hover:bg-[#e05e00] transition-colors shrink-0 no-underline"
		>
			<span class="lucide-download size-3.5" />
			<span>{{ __('Download PDF') }}</span>
		</a>
	</div>
	<!-- Keyed on the block text, not just the index: position N of the outgoing
	     lesson and position N of the incoming one share an index, so Vue reuses
	     the instance and hands a <PdfBlock> a new `file`, which it only reads
	     once, at setup. Including the text forces a fresh instance. -->
	<div
		v-for="(block, index) in content?.split('\n\n')"
		:key="`${index}:${block}`"
	>
		<div v-if="block.includes('{{ YouTubeVideo')">
			<div
				v-if="youtubeEmbedId(getId(block))"
				:key="youtubeEmbedId(getId(block))"
				class="not-prose my-5 overflow-hidden rounded-7 border border-outline-gray-2"
			>
				<div
					class="video-player"
					data-plyr-provider="youtube"
					:data-plyr-embed-id="youtubeEmbedId(getId(block))"
				></div>
			</div>
		</div>
		<div v-else-if="block.includes('{{ Quiz')">
			<Quiz :quiz="getId(block)" />
		</div>
		<div
			v-else-if="block.includes('{{ Video')"
			class="not-prose my-5 overflow-hidden rounded-7 border border-outline-gray-2"
		>
			<video
				:ref="guardMacroVideo"
				controls
				width="100%"
				class="block w-full"
				controlsList="nodownload"
				oncontextmenu="return false;"
			>
				<source :src="safeUrl(getId(block))" type="video/mp4" />
			</video>
		</div>
		<div v-else-if="block.includes('{{ PDF')">
			<PdfBlock v-if="inlinePdf" :file="getId(block)" />
			<div
				v-else
				class="not-prose my-5 overflow-hidden rounded-7 border border-outline-gray-2"
			>
				<iframe
					:src="safeUrl(getId(block))"
					:title="__('PDF document')"
					width="100%"
					height="700px"
					class="block"
					type="application/pdf"
				></iframe>
			</div>
		</div>
		<div
			v-else-if="block.includes('{{ Audio')"
			class="not-prose my-5 overflow-hidden rounded-7 border border-outline-gray-2"
		>
			<audio
				width="100%"
				class="block w-full"
				controls
				controlsList="nodownload"
			>
				<source :src="safeUrl(getId(block))" type="audio/mp3" />
			</audio>
		</div>
		<div
			v-else-if="block.includes('{{ Embed')"
			class="not-prose my-5 overflow-hidden rounded-7 border border-outline-gray-2"
		>
			<iframe
				width="100%"
				height="400"
				class="block"
				:src="safeUrl(getId(block))"
				:title="__('Embedded content')"
				frameborder="0"
				allowfullscreen
			>
			</iframe>
		</div>
		<div v-else v-safe-html:rich="renderMarkdown(block)"></div>
	</div>
	<div v-if="quizId">
		<Quiz :quiz="quizId" />
	</div>
</template>
<script setup lang="ts">
import type { ComponentPublicInstance } from 'vue'
import Quiz from '@/components/QuizBlock.vue'
import PdfBlock from '@/components/PdfBlock.vue'
// @ts-expect-error markdown-it ships no type declarations
import MarkdownIt from 'markdown-it'
import { extractYoutubeID, getMacroArg } from '@/utils/lessonMacros'
import { usesWebkitPdfViewer } from '@/utils/pdfViewer'
import { safeUrl } from '@/utils/safeUrl'
import { guardVideoElementSkips } from '@/utils/videoSkipGuard'

const inlinePdf = usesWebkitPdfViewer()

const markdown = new MarkdownIt({
	html: true,
	linkify: true,
})

// The directive sanitizes at the rich level, which is where the anchor-target
// hook and the form-tag blocklist live. This only does the markdown pass.
const renderMarkdown = (block: string): string => markdown.render(block)

defineProps<{
	content?: string
	youtube?: string
	vimeoUrl?: string
	videoFile?: string
	attachment?: string
	quizId?: string
}>()

const vimeoEmbedUrl = (url: string | undefined): string => {
	if (!url) return ''
	const match = url.match(/(?:vimeo\.com\/)(\d+)/)
	return match ? `https://player.vimeo.com/video/${match[1]}?title=0&byline=0&portrait=0` : ''
}

const getId = (block: string): string => {
	// Guard the match: a malformed `{{ PDF() }}` / unbalanced-quote macro yields
	// null, and the old unguarded [1] threw and killed the whole lesson render.
	return getMacroArg(block) ?? ''
}

const guardMacroVideo = (
	el: Element | ComponentPublicInstance | null
): void => {
	if (el instanceof HTMLVideoElement) guardVideoElementSkips(el)
}

// Both authoring paths (the `youtube` field and the `{{ YouTubeVideo }}` macro)
// must land in the same Plyr-wrapped `.video-player` the EditorJS embed block
// renders. A bare <iframe> is invisible to the watch tracker in Lesson.vue, so
// enforce_video_completion saw "no video" and auto-completed on the dwell timer.
// Falsy id => render nothing rather than a Plyr player with no video, which
// would suppress the dwell timer and leave the lesson uncompletable.
const youtubeEmbedId = (source: string | undefined): string =>
	source ? extractYoutubeID(source) : ''
</script>

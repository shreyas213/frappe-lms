import { createRouter, createWebHistory } from 'vue-router'
import { call } from 'frappe-ui'
import { usersStore } from './stores/user'
import { sessionStore } from './stores/session'
import { useSettings } from './stores/settings'
import { getLmsBasePath } from './utils/basePath'
import { routes } from './routes'

// Run the fresh-site-admin persona check at most once per app load.
let personaChecked = false

async function shouldCapturePersona() {
	const captured = await call('frappe.client.get_single_value', {
		doctype: 'LMS Settings',
		field: 'persona_captured',
	})
	if (captured) return false
	const courseCount = await call('frappe.client.get_count', {
		doctype: 'LMS Course',
		filters: {
			title: ['not like', '%A guide to Frappe Learning%'],
		},
	})
	return !courseCount
}

let router = createRouter({
	history: createWebHistory(`/${getLmsBasePath()}`),
	routes,
})

router.beforeEach(async (to, from, next) => {
	const { userResource } = usersStore()
	const session = sessionStore()
	const { settings } = useSettings()

	try {
		if (session.isLoggedIn || !userResource.fetched) {
			await userResource.promise
		}
	} catch (error) {
		// Ignore transient auth errors
	}

	const isUserLoggedIn =
		session.isLoggedIn ||
		Boolean(userResource.data?.name && userResource.data.name !== 'Guest')

	if (!isUserLoggedIn) {
		const protectedRoutes = [
			'Home',
			'Statistics',
			'Profile',
			'ProfileAbout',
			'ProfileCertificates',
			'ProfileRoles',
			'ProfileEvaluator',
			'ProfileEvaluationSchedule',
			'Billing',
			'Lesson',
			'CourseCertification',
			'SCORMChapter',
			'NewCourse',
			'CourseImport',
			'ChapterForm',
			'NewCourseEnrollment',
			'NewBatch',
			'BulkCertificates',
			'NewLiveClass',
			'NewAnnouncement',
			'NewBatchCourse',
			'NewAssessment',
			'NewBatchStudent',
			'NewBatchEmailTemplate',
			'Assignments',
			'NewAssignment',
			'AssignmentForm',
			'AssignmentSubmissions',
			'AssignmentSubmission',
			'ProgrammingExercises',
			'NewProgrammingExercise',
			'ProgrammingExerciseForm',
			'ProgrammingExerciseSubmissions',
			'ProgrammingExerciseSubmission',
			'DataImportList',
			'NewDataImport',
			'DataImport',
			'MemberForm',
			'MobileYou',
		]
		if (protectedRoutes.includes(to.name)) {
			window.location.replace('/login')
			return
		}

		try {
			await settings.promise
		} catch (e) {}
		if (settings.data && !settings.data.allow_guest_access) {
			window.location.replace('/login')
			return
		}
	}

	if (
		isUserLoggedIn &&
		!personaChecked &&
		to.name !== 'PersonaForm' &&
		userResource.data?.is_system_manager &&
		!userResource.data?.developer_mode
	) {
		personaChecked = true
		try {
			if (await shouldCapturePersona()) {
				return next({ name: 'PersonaForm' })
			}
		} catch (_) {
			// Fail open: a transient API error must not block navigation.
		}
	}

	return next()
})

export default router

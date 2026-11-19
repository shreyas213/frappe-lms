import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { usersStore } from './user'
import { forgetContinuePanelClosed } from '@/utils/continuePanel'
import { computed, reactive, ref, watch } from 'vue'

export const sessionStore = defineStore('lms-session', () => {
	let { userResource } = usersStore()
	const brand = reactive({})

	function sessionUser() {
		let cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
		let _sessionUser = cookies.get('user_id')
		if (_sessionUser) {
			_sessionUser = decodeURIComponent(_sessionUser).replace(/^"(.*)"$/, '$1')
		}
		if (!_sessionUser || _sessionUser === 'Guest') {
			_sessionUser = null
		} else {
			userResource.reload()
		}
		return _sessionUser
	}

	let user = ref(sessionUser())
	const isLoggedIn = computed(() => {
		if (userResource.data?.name && userResource.data.name !== 'Guest') {
			return true
		}
		return !!user.value && user.value !== 'Guest'
	})

	watch(
		() => userResource.data,
		(val) => {
			if (val && val.name && val.name !== 'Guest') {
				user.value = val.name
			} else if (val && val.name === 'Guest') {
				user.value = null
			}
		}
	)

	const logout = createResource({
		url: 'logout',
		onSuccess() {
			userResource.reset()
			user.value = null
			// A closed continue-your-course panel comes back on the next sign-in.
			forgetContinuePanelClosed()
			window.location.replace('/login')
		},
		onError() {
			userResource.reset()
			user.value = null
			window.location.replace('/login')
		},
	})

	const branding = createResource({
		url: 'lms.lms.api.get_branding',
		cache: 'brand',
		auto: true,
		onSuccess(data) {
			brand.name = data.app_name
			brand.logo = data.app_logo
			brand.favicon =
				data.favicon?.file_url || '/assets/lms/frontend/learning.svg'
		},
	})

	return {
		user,
		isLoggedIn,
		logout,
		brand,
		branding,
	}
})

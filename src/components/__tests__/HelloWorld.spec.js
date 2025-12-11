import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HelloWorld from '../HelloWorld.vue'

describe('HelloWorld', () => {
  it('renders properly', () => {
    const wrapper = mount(HelloWorld, { props: { msg: 'Test Message', description: 'Test Description' } })
    expect(wrapper.text()).toContain('Test Message')
    expect(wrapper.text()).toContain('Test Description')
  })

  it('displays the correct message', () => {
    const msg = 'Test Message'
    const wrapper = mount(HelloWorld, { props: { msg, description: 'Test Description' } })
    expect(wrapper.find('h1').text()).toBe(msg)
  })
})
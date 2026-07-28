import { pageState } from "./page"
import { reactive } from "vue"
import { du } from "./base"

export const menuModule = {
    toggleMenu() {
        if (pageState.isMenuClosed) {
            pageState.leftUp = { transform: 'scale(0.8)' }
            pageState.leftDown = { transform: `translateY(${du(68.65)}) scale(0.8)` }
            pageState.rightUp = { transform: `translateX(${du(43.7)}) scale(0.8)` }
            pageState.rightDown = { transform: `translate(${du(43.7)}, ${du(68.65)}) scale(0.8)` }
            pageState.menuBox = { zIndex: '21', opacity: '1', transform: 'scale(0.8,0.8)' }
        } else {
            pageState.leftUp = {}
            pageState.leftDown = {}
            pageState.rightUp = {}
            pageState.rightDown = {}
            pageState.menuBox = { zIndex: '23', opacity: '0', transform: 'scale(0.1,0.067)' }
        }
        pageState.isMenuClosed = !pageState.isMenuClosed
    }
}
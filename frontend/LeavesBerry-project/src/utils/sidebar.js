import { ref, reactive } from 'vue'
import { du } from './base';

export const arrowStyle = reactive({ transform: "" })


export function switchArrow(sn) {
    const arrowTransfrom = 10 * sn;
    arrowStyle.transform = `translateY(calc(${du(arrowTransfrom)} + calc(${sn} * 1.1px)))`
}
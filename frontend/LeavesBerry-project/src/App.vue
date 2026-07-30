<template>
  <div id="app-root">

    <div id="page-filter" v-if="pageState.showFilter"></div>

    <div ref="qrBox" style="display: none;"></div>

    <div id="menu-box" :class="pageState.isMenuClosed ? 'parent-prevent' : ''" @click="menuModule.toggleMenu"
      :style="pageState.menuBox">

      <div id="user_info">
        <img id="avatar" :src="userState.avatarUrl" @click="userModule.changeAvatar">
        <p id="name">{{ userState.userName }}</p>
        <p id="bio" @click="userModule.changeBio">{{ userState.bio }}</p>
        <div id="level">
          <p>XP: Lv{{ userState.level }}</p>
          <div>
            <line :style="{ width: `${(userState.xp / 1000) * 100}%` }"></line>
          </div>
        </div>
      </div>


      <span class="star s1">✦</span>
      <span class="star s2">✦</span>
      <span class="star s3">✦</span>
      <span class="star s4">✦</span>
      <span class="star s5">✦</span>
      <span class="star s6">✦</span>
      <span class="star s7">✦</span>
      <span class="star s8">✦</span>


      <svg width="100%" height="100%">
        <line x1="27.2px" y1="11px" x2="250px" y2="11px" stroke="#73B436" stroke-width="1" />
        <line x1="10px" y1="27.42px" x2="10px" y2="392px" stroke="#73B436" stroke-width="1" />
        <line x1="268px" y1="27.42px" x2="268px" y2="392px" stroke="#73B436" stroke-width="1" />
        <line x1="27.2px" y1="410px" x2="250" y2="410px" stroke="#73B436" stroke-width="1" />
        <line x1="10px" y1="100px" x2="268px" y2="100px" stroke="#73B436" stroke-width="1" />
      </svg>

      <div id="menu-function-button-box">
        <button class="menu-function-button">
          <svg class="menu-function-icon" viewBox="0 0 32 32" aria-hidden="true">
            <rect x="4" y="7" width="24" height="18" rx="2"></rect>
            <path d="M5 9l11 8 11-8"></path>
          </svg>
          <span>邮箱</span>
        </button>

        <button class="menu-function-button" @click="goPage('/Collect')">
          <svg class="menu-function-icon" viewBox="0 0 32 32" aria-hidden="true">
            <path d="M16 4.5l3.5 7.1 7.8 1.1-5.6 5.5 1.3 7.8-7-3.7-7 3.7 1.3-7.8-5.6-5.5 7.8-1.1z"></path>
          </svg>
          <span>收藏夹</span>
        </button>

        <button class="menu-function-button" @click="goPage('/Setting')">
          <svg class="menu-function-icon" viewBox="0 0 32 32" aria-hidden="true">
            <circle cx="16" cy="16" r="4"></circle>
            <path
              d="M16 3.5v4M16 24.5v4M3.5 16h4M24.5 16h4M7.2 7.2l2.8 2.8M22 22l2.8 2.8M24.8 7.2L22 10M10 22l-2.8 2.8">
            </path>
            <circle cx="16" cy="16" r="9"></circle>
          </svg>
          <span>设置</span>
        </button>

        <button class="menu-function-button" @click="goPage('/')">
          <svg class="menu-function-icon" viewBox="0 0 32 32" aria-hidden="true">
            <path d="M5 15.5L16 6l11 9.5"></path>
            <path d="M8 14v12h16V14M13 26v-7h6v7"></path>
          </svg>
          <span>主页</span>
        </button>

        <button class="menu-function-button" @click="goPage('/Announce')">
          <svg class="menu-function-icon" viewBox="0 0 32 32" aria-hidden="true">
            <path d="M5 14v5h5l11 5V9l-11 5z"></path>
            <path d="M10 19l2 7h4l-2-6M24 12c2 2 2 6 0 8"></path>
          </svg>
          <span>公告栏</span>
        </button>

        <button class="menu-function-button" @click="goPage('/History')">
          <svg class="menu-function-icon" viewBox="0 0 32 32" aria-hidden="true">
            <circle cx="16" cy="16" r="11"></circle>
            <path d="M16 9v7l5 3"></path>
          </svg>
          <span>历史</span>
        </button>

        <button class="menu-function-button">
          <svg class="menu-function-icon" viewBox="0 0 32 32" aria-hidden="true">
            <circle cx="16" cy="16" r="11"></circle>
            <path d="M12.5 12a3.7 3.7 0 017-1.7c1.4 3.4-3.5 4.1-3.5 7.2"></path>
            <path d="M16 23h.01"></path>
          </svg>
          <span>帮助</span>
        </button>

        <button class="menu-function-button" @click="goPage('/Feedback')">
          <span class="menu-function-symbol" aria-hidden="true">@</span>
          <span>反馈箱</span>
        </button>

        <button class="menu-function-button" @click="goPage('/Protocol')">
          <span class="menu-function-symbol" aria-hidden="true">#</span>
          <span>协议</span>
        </button>

        <button class="menu-function-button" style="border-radius:0 0 0 3vh">
          <svg class="menu-function-icon" viewBox="0 0 32 32" aria-hidden="true">
            <path d="M7 17l6 6L25 9"></path>
          </svg>
          <span>测试</span>
        </button>

        <button class="menu-function-button" @click="goPage('/CmdColumn')">
          <span class="menu-function-symbol menu-function-symbol--code" aria-hidden="true">&lt;/&gt;</span>
          <span>指令表</span>
        </button>

        <button class="menu-function-button" @click="userState.isLogined ?
          loginModule.logout() : (loginModule.openLoginWindow(), loginModule.memberEnter())" 
          style="border-radius:0 0 3vh 0">
          <svg class="menu-function-icon" viewBox="0 0 32 32" aria-hidden="true">
            <path d="M27 16H7M14 9l-7 7 7 7"></path>
          </svg>
          <span>{{ userState.isLogined ? '登出' : '登入' }}</span>
        </button>
      </div>
    </div>

    <button class="menu-button" id="button-left-up" :style="pageState.leftUp"></button>
    <button class="menu-button" id="button-left-down" :style="pageState.leftDown"></button>
    <button class="menu-button" id="button-right-up" :style="pageState.rightUp"></button>
    <button class="menu-button" id="button-right-down" :style="pageState.rightDown"></button>

    <p class="tip" :style="tip.tipStyle">{{ tip.tipText }}</p>

    <div id="navbar" :style="pageState.navbar">

      <input id="search-input" type="text" placeholder="查找……" v-model="pageState.searchKey" />
      <button id="search-button" @click="navbarModule.DoSearch">GO</button>

      <div id="navbar-fuction-button-box">
        <!-------------截图-------------->
        <button class="navbar-function-button" id="scrshot-button" @click="navbarModule.handleScreenshot">✦</button>
        <img id="screen-shot" v-if="pageState.isScrShot" :src="pageState.scrShot">
        <!-------------收藏-------------->
        <button class="navbar-function-button" id="collect-button"
          :style="{ color: pageState.isCollected ? '#73B436' : 'rgb(90,25,27)' }"
          @click="navbarModule.toggleColl">✦</button>
        <!-------------分享-------------->
        <button class="navbar-function-button" id="share-button" @click="navbarModule.toggleShare"
          :style="pageState.shareStyle">{{ pageState.shareText }}</button>
        <!-------------指令-------------->
        <button class="navbar-function-button" id="command-button"
          :style="{ color: !pageState.isCmdClosed ? 'red' : '#5A191B' }" @click="navbarModule.toggleCmdUI">/</button>
      </div>

      <div id="command-menu" v-if="!pageState.isCmdClosed">
        <p id="command-title">指令面板</p>
        <button id="close-command" @click="navbarModule.toggleCmdUI">×</button>
        <input id="cmd-input" v-model="pageState.cmdInputValue" @keyup.enter="navbarModule.executeCmd(cmdOutputBox)"
        placeholder="请输入指令 | 按键盘<Enter>或右侧<RUN>执行">
        <button id="execute-cmd-button" @click="navbarModule.executeCmd(cmdOutputBox)">RUN</button>
        <div id="cmd-output-box" ref="cmdOutputBox">
          <p id="cmd-output">{{ pageState.cmdOutputText }}</p>
        </div>
      </div>
    </div>




    <div id="login-window" :style="loginModule.window">
      <!--复用visitorEntry属性更为方便-->
      <div id="enter-tip" :style="loginModule.visitorEntry">
        <p>-----选择您进入本站的方式-----</p>
      </div>

      <div id="visitor-entry" @click="loginModule.visitorEnter" :style="loginModule.visitorEntry">
        <p id="identification">❖访客❖</p>
        <div class="entry-person entry-person--visitor" aria-hidden="true">
          <span class="entry-person__head"></span>
          <span class="entry-person__neck"></span>
          <span class="entry-person__body"></span>
        </div>
      </div>
      <div id="member-entry" @click="loginModule.memberEnter" :style="loginModule.memberEntry">
        <p id="identification" :style="loginModule.visitorEntry">❖成员❖</p>
        <div class="entry-person entry-person--member" aria-hidden="true" :style="loginModule.memberSign">
          <span class="entry-person__sparkle"></span>
          <span class="entry-person__head"></span>
          <span class="entry-person__neck"></span>
          <span class="entry-person__body"></span>
        </div>
        <div id="info-input" :style="loginModule.infoInput">
          <button id="rechoose" @click.stop="loginModule.rechoose">返回</button>
          <input id="input-email" v-model="loginModule.inputEmail" placeholder="邮箱"></input>
          <input id="input-code" v-model="loginModule.inputCode" placeholder="验证码--仅注册须填"></input>
          <input id="input-name" v-model="loginModule.inputName" placeholder="名称--仅注册须填"></input>
          <input id="input-password" v-model="loginModule.inputPw" placeholder="密码"></input>
          <button id="register" @click="loginModule.register">注册</button>
          <button id="login" @click="loginModule.login">登录</button>
        </div>
      </div>
    </div>

    <div id="teleport-root"></div>

    <router-view v-slot="{ Component, route }">
      <transition name="page-cover-slide">
        <div :key="route.fullPath" class="page-cover-slide-view">
          <component :is="Component" />
        </div>
      </transition>
    </router-view>
  </div>
</template>
<script setup>
import axios from 'axios';
import { ref, onMounted, onUnmounted, watch, reactive } from 'vue';
import {
  debounce, tip, onGlobalClick, useGoPage,
  navbarModule, menuModule, pageState, routeListener,
  userState, userModule, loginModule, qrBox, startTimer
} from './utils/index';
import { useHead } from "@vueuse/head"

const { goPage, backPage, goPageByName } = useGoPage()

const cmdOutputBox = ref(null)

useHead({
  title: () => pageState.currentTitle,
  meta: [{ name: "description", content: () => pageState.currentDesc }]
})


// ------------------------------
// 生命周期
// ------------------------------
onMounted(() => {
  routeListener();
  startTimer();
  userModule.initUser();
  document.addEventListener('click', onGlobalClick);
})

onUnmounted(() => {
  document.removeEventListener('click', onGlobalClick);
})
</script>
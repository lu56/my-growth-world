/**
 * Web Audio API 8-bit 芯片音效系统
 * 零音频文件，纯代码生成像素游戏风格音效
 */

let audioCtx: AudioContext | null = null
let enabled = true

function getCtx(): AudioContext | null {
  if (!enabled) return null
  if (!audioCtx) {
    try {
      audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)()
    } catch {
      return null
    }
  }
  // 浏览器策略：需要用户交互后才能恢复
  if (audioCtx.state === 'suspended') {
    audioCtx.resume()
  }
  return audioCtx
}

export function setSoundEnabled(val: boolean) {
  enabled = val
}

export function isSoundEnabled() {
  return enabled
}

interface ToneOptions {
  freq: number
  duration: number
  type?: OscillatorType
  volume?: number
  startTime?: number
  sweepTo?: number  // 频率扫描终点
}

function tone(ctx: AudioContext, opts: ToneOptions) {
  const {
    freq,
    duration,
    type = 'square',
    volume = 0.15,
    startTime = 0,
    sweepTo,
  } = opts

  const osc = ctx.createOscillator()
  const gain = ctx.createGain()

  osc.type = type
  osc.frequency.setValueAtTime(freq, ctx.currentTime + startTime)

  if (sweepTo) {
    osc.frequency.exponentialRampToValueAtTime(
      sweepTo,
      ctx.currentTime + startTime + duration
    )
  }

  // ADSR 包络
  gain.gain.setValueAtTime(0, ctx.currentTime + startTime)
  gain.gain.linearRampToValueAtTime(volume, ctx.currentTime + startTime + 0.01)
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + startTime + duration)

  osc.connect(gain)
  gain.connect(ctx.destination)

  osc.start(ctx.currentTime + startTime)
  osc.stop(ctx.currentTime + startTime + duration)
}

/**
 * 播放指定音效
 * @param name 音效名称
 */
export function playSound(name: 'gem' | 'levelup' | 'achievement' | 'exchange' | 'click' | 'penalty') {
  const ctx = getCtx()
  if (!ctx) return

  switch (name) {
    case 'gem':
      // 加分：清脆上升音 C5→E5→G5
      tone(ctx, { freq: 523, duration: 0.08, type: 'square', volume: 0.12 })
      tone(ctx, { freq: 659, duration: 0.08, type: 'square', volume: 0.12, startTime: 0.06 })
      tone(ctx, { freq: 784, duration: 0.12, type: 'square', volume: 0.12, startTime: 0.12 })
      break

    case 'levelup':
      // 升级：宏伟上升音阶 C5→E5→G5→C6 + 持续和弦
      tone(ctx, { freq: 523, duration: 0.1, type: 'square', volume: 0.15 })
      tone(ctx, { freq: 659, duration: 0.1, type: 'square', volume: 0.15, startTime: 0.08 })
      tone(ctx, { freq: 784, duration: 0.1, type: 'square', volume: 0.15, startTime: 0.16 })
      tone(ctx, { freq: 1047, duration: 0.3, type: 'square', volume: 0.18, startTime: 0.24 })
      tone(ctx, { freq: 523, duration: 0.4, type: 'triangle', volume: 0.08, startTime: 0.24 })
      tone(ctx, { freq: 659, duration: 0.4, type: 'triangle', volume: 0.08, startTime: 0.24 })
      break

    case 'achievement':
      // 成就解锁：闪亮音 + 上升琶音
      tone(ctx, { freq: 1568, duration: 0.06, type: 'square', volume: 0.1 })
      tone(ctx, { freq: 2093, duration: 0.08, type: 'square', volume: 0.1, startTime: 0.04 })
      tone(ctx, { freq: 523, duration: 0.1, type: 'square', volume: 0.12, startTime: 0.1 })
      tone(ctx, { freq: 659, duration: 0.1, type: 'square', volume: 0.12, startTime: 0.18 })
      tone(ctx, { freq: 784, duration: 0.1, type: 'square', volume: 0.12, startTime: 0.26 })
      tone(ctx, { freq: 1047, duration: 0.2, type: 'square', volume: 0.15, startTime: 0.34 })
      break

    case 'exchange':
      // 兑换：金币叮当声
      tone(ctx, { freq: 1319, duration: 0.06, type: 'square', volume: 0.12 })
      tone(ctx, { freq: 1568, duration: 0.06, type: 'square', volume: 0.12, startTime: 0.05 })
      tone(ctx, { freq: 2093, duration: 0.15, type: 'square', volume: 0.14, startTime: 0.1 })
      tone(ctx, { freq: 1047, duration: 0.2, type: 'triangle', volume: 0.08, startTime: 0.1 })
      break

    case 'click':
      // 点击：短促方块音
      tone(ctx, { freq: 800, duration: 0.03, type: 'square', volume: 0.08 })
      break

    case 'penalty':
      // 减分：下降音 G4→C4
      tone(ctx, { freq: 392, duration: 0.1, type: 'sawtooth', volume: 0.1 })
      tone(ctx, { freq: 262, duration: 0.15, type: 'sawtooth', volume: 0.1, startTime: 0.08 })
      break
  }
}

import type { InputHTMLAttributes } from 'react';
import { useId } from 'react';

interface SliderProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  onChange: (value: number) => void;
  error?: string;
  showInput?: boolean;
}

export function Slider({
  label,
  value,
  min,
  max,
  step = 1,
  unit = '',
  onChange,
  error,
  showInput = true,
  className = '',
}: SliderProps) {
  const id = useId();
  const percentage = ((value - min) / (max - min)) * 100;

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex justify-between items-center">
        <label htmlFor={id} className="text-sm font-medium text-secondary-on-container">
          {label}
        </label>
        {showInput && (
          <div className="flex items-center gap-1">
            <input
              type="number"
              value={value}
              min={min}
              max={max}
              step={step}
              onChange={(e) => {
                const newValue = parseFloat(e.target.value);
                if (!isNaN(newValue) && newValue >= min && newValue <= max) {
                  onChange(newValue);
                }
              }}
              className="w-20 px-2 py-1 text-sm text-right bg-surface border border-secondary-container/50
                         rounded text-primary-on-container focus:outline-none focus:ring-1 focus:ring-primary/50"
              aria-label={`${label} value`}
            />
            {unit && <span className="text-sm text-secondary">{unit}</span>}
          </div>
        )}
      </div>

      <div className="relative">
        <input
          id={id}
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="w-full h-2 rounded-full appearance-none cursor-pointer
                     bg-secondary-container/30 accent-primary
                     [&::-webkit-slider-thumb]:appearance-none
                     [&::-webkit-slider-thumb]:w-5
                     [&::-webkit-slider-thumb]:h-5
                     [&::-webkit-slider-thumb]:rounded-full
                     [&::-webkit-slider-thumb]:bg-primary
                     [&::-webkit-slider-thumb]:shadow-lg
                     [&::-webkit-slider-thumb]:shadow-primary/30
                     [&::-webkit-slider-thumb]:cursor-pointer
                     [&::-webkit-slider-thumb]:transition-transform
                     [&::-webkit-slider-thumb]:hover:scale-110
                     [&::-moz-range-thumb]:w-5
                     [&::-moz-range-thumb]:h-5
                     [&::-moz-range-thumb]:border-0
                     [&::-moz-range-thumb]:rounded-full
                     [&::-moz-range-thumb]:bg-primary
                     [&::-moz-range-thumb]:shadow-lg
                     [&::-moz-range-thumb]:cursor-pointer"
          style={{
            background: `linear-gradient(to right, var(--primary) 0%, var(--primary) ${percentage}%, var(--secondary-container) ${percentage}%, var(--secondary-container) 100%)`,
          }}
          aria-valuenow={value}
          aria-valuemin={min}
          aria-valuemax={max}
        />
        <div className="flex justify-between text-xs text-secondary mt-1">
          <span>{min}{unit}</span>
          <span>{max}{unit}</span>
        </div>
      </div>

      {error && (
        <p className="text-sm text-error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

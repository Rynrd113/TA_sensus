import { useState, useCallback, ChangeEvent } from 'react';

interface FormField {
  [key: string]: any;
}

interface FormErrors {
  [key: string]: string;
}

interface UseFormOptions<T> {
  initialValues: T;
  validationRules?: {
    [K in keyof T]?: (value: T[K]) => string | null;
  };
  onSubmit?: (values: T) => Promise<void> | void;
}

interface UseFormReturn<T> {
  values: T;
  errors: FormErrors;
  loading: boolean;
  handleChange: (name: keyof T) => (event: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => void;
  handleSubmit: (event?: React.FormEvent) => Promise<void>;
  setFieldValue: (name: keyof T, value: any) => void;
  setFieldError: (name: keyof T, error: string) => void;
  clearErrors: () => void;
  resetForm: () => void;
  isValid: boolean;
}

export function useForm<T extends FormField>({
  initialValues,
  validationRules = {},
  onSubmit
}: UseFormOptions<T>): UseFormReturn<T> {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);

  // Validasi single field
  const validateField = useCallback((name: keyof T, value: any): string | null => {
    const validator = validationRules[name];
    return validator ? validator(value) : null;
  }, [validationRules]);

  // Validasi semua field
  const validateForm = useCallback((): boolean => {
    const newErrors: FormErrors = {};
    let isFormValid = true;

    Object.keys(values).forEach((key) => {
      const error = validateField(key as keyof T, values[key]);
      if (error) {
        newErrors[key] = error;
        isFormValid = false;
      }
    });

    setErrors(newErrors);
    return isFormValid;
  }, [values, validateField]);

  // Handle perubahan input
  const handleChange = useCallback((name: keyof T) => {
    return (event: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
      const { value, type } = event.target;
      
      // Handle different input types
      let parsedValue: any = value;
      if (type === 'number') {
        parsedValue = value === '' ? '' : Number(value);
      } else if (type === 'checkbox') {
        parsedValue = (event.target as HTMLInputElement).checked;
      }

      setValues(prev => ({
        ...prev,
        [name]: parsedValue
      }));

      // Clear error untuk field ini jika ada
      if (errors[name as string]) {
        setErrors(prev => ({
          ...prev,
          [name as string]: ''
        }));
      }

      // Validasi real-time
      const error = validateField(name, parsedValue);
      if (error) {
        setErrors(prev => ({
          ...prev,
          [name as string]: error
        }));
      }
    };
  }, [errors, validateField]);

  // Set value secara manual
  const setFieldValue = useCallback((name: keyof T, value: any) => {
    setValues(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear error
    if (errors[name as string]) {
      setErrors(prev => ({
        ...prev,
        [name as string]: ''
      }));
    }
  }, [errors]);

  // Set error secara manual
  const setFieldError = useCallback((name: keyof T, error: string) => {
    setErrors(prev => ({
      ...prev,
      [name as string]: error
    }));
  }, []);

  // Clear semua errors
  const clearErrors = useCallback(() => {
    setErrors({});
  }, []);

  // Reset form ke initial values
  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setLoading(false);
  }, [initialValues]);

  // Handle submit
  const handleSubmit = useCallback(async (event?: React.FormEvent) => {
    if (event) {
      event.preventDefault();
    }

    if (!validateForm()) {
      return;
    }

    if (onSubmit) {
      try {
        setLoading(true);
        await onSubmit(values);
      } catch (error: any) {
        // Handle submit error
        console.error('Form submission error:', error);
        
        // Jika error dari server berupa field-specific errors
        if (error.response?.data?.errors) {
          setErrors(error.response.data.errors);
        }
      } finally {
        setLoading(false);
      }
    }
  }, [validateForm, onSubmit, values]);

  // Check apakah form valid
  const isValid = Object.keys(errors).every(key => !errors[key]);

  return {
    values,
    errors,
    loading,
    handleChange,
    handleSubmit,
    setFieldValue,
    setFieldError,
    clearErrors,
    resetForm,
    isValid
  };
}

export default useForm;
